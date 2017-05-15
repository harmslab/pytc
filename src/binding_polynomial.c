#include "binding_polynomial.h"
#include <math.h>
#include <stdlib.h>
#define MIN(a, b) ((a) < (b) ? (a) : (b))

double dQdT(double T_free, double S_total, double T_total, double *fit_beta_obj, int num_beta){
    /*
    T_total = T_free + S_total*(dln(P)/dln(T_free)), so:
        0 = T_free + S_total*(dln(P)/dln(T_free)) - T_total

        Solve this for T_free to find free titrant.

        dln(P)/dln(T_free)

        P = (beta1*T_free**1) *  b2*T**2 
    */
    int i;
    double numerator, denominator;

    // should be array
    numerator = 0;
    denominator = 1;
    for (i = 0; i < num_beta; i++){
        double bt = fit_beta_obj[i]*pow(T_free,i); 
        numerator   += (i+1)*bt;
        denominator +=       bt;
    }

    double P = numerator/denominator;

    return T_free + S_total*P - T_total;

}

double brentq(callback_type f, double xa, double xb, double *args) {
    double xpre = xa, xcur = xb;
    double xblk = 0., fpre, fcur, fblk = 0., spre = 0., scur = 0., sbis;
    double xtol = 2e-12;
    /* 4*finfo(float).eps */
    double rtol = 8.8817841970012523e-16;
    /* the tolerance is 2*delta */
    double delta;
    double stry, dpre, dblk;
    int i;

    fpre = (*f)(xpre, args);
    fcur = (*f)(xcur, args);
    int funcalls = 2;
    if (fpre*fcur > 0) {
        return 0.;
    }
    if (fpre == 0) {
        return xpre;
    }
    if (fcur == 0) {
        return xcur;
    }

    int iterations = 0;
    int iter = 100;
    for (i = 0; i < iter; i++) {
        iterations++;
        if (fpre*fcur < 0) {
            xblk = xpre;
            fblk = fpre;
            spre = scur = xcur - xpre;
        }
        if (fabs(fblk) < fabs(fcur)) {
            xpre = xcur;
            xcur = xblk;
            xblk = xpre;

            fpre = fcur;
            fcur = fblk;
            fblk = fpre;
        }

        delta = (xtol + rtol*fabs(xcur))/2;
        sbis = (xblk - xcur)/2;
        if (fcur == 0 || fabs(sbis) < delta) {
            return xcur;
        }

        if (fabs(spre) > delta && fabs(fcur) < fabs(fpre)) {
            if (xpre == xblk) {
                /* interpolate */
                stry = -fcur*(xcur - xpre)/(fcur - fpre);
            }
            else {
                /* extrapolate */
                dpre = (fpre - fcur)/(xpre - xcur);
                dblk = (fblk - fcur)/(xblk - xcur);
                stry = -fcur*(fblk*dblk - fpre*dpre)
                    /(dblk*dpre*(fblk - fpre));
            }
            if (2*fabs(stry) < MIN(fabs(spre), 3*fabs(sbis) - delta)) {
                /* good short step */
                spre = scur;
                scur = stry;
            } else {
                /* bisect */
                spre = sbis;
                scur = sbis;
            }
        }
        else {
            /* bisect */
            spre = sbis;
            scur = sbis;
        }

        xpre = xcur; fpre = fcur;
        if (fabs(scur) > delta) {
            xcur += scur;
        }
        else {
            xcur += (sbis > 0 ? delta : -delta);
        }

        fcur = (*f)(xcur, args);
        funcalls++;
    }
    return xcur;
}

float dQ(double *fit_beta_obj, double *fit_dH_obj, double *S_conc_corr, double *T_conc, 
            double *T_conc_free, double cell_volume, double *dilution_heats, 
            int num_sites, int num_shots, int size_T_conc, int size_S_conc){

    double min_value, max_value;
    int i;
    float DELTA = 0.0, TOLERANCE = 1e-9;
    
    for (i = 0; i < num_shots; i++){

        if (fabs(T_conc[i] - DELTA) < TOLERANCE){
            T_conc_free[i] = 0.0;
            continue;
        }
        
        //S_conc_corr = S_conc[i]*fx_competent;

        min_value = dQdT(0.0,S_conc_corr[i],T_conc[i], fit_beta_obj, num_sites);
        max_value = dQdT(T_conc[i],S_conc_corr[i],T_conc[i], fit_beta_obj, num_sites);
            
        // Uh oh, they have same sign (root optimizer will choke)
        if (min_value*max_value > 0){

            if (max_value < 0){
                // root is closest to min --> set to that
                if (max_value < min_value) {
                    T_conc_free[i] = 0.0;
                // root is closest to max --> set to that
                } else {
                    T_conc_free[i] = T_conc[i];
                }
            } else {
                // root is closest to max --> set to that
                if (max_value < min_value){
                    T_conc_free[i] = T_conc[i];

                // root is closest to min --> set to that
                } else {
                    T_conc_free[i] = 0.0;
                }
            }
            continue;
        }
        
        double args[2] = {S_conc_corr[i], T_conc[i]};
        int lastT = size_T_conc - 1;
        double T = brentq(dQdT, 0 , T_conc[lastT], args);

        // numerical problems sometimes make T slightly bigger than the total
        // concentration, so bring down to the correct value
        if (T > T_conc[i]) { T = T_conc[i]; }
        T_conc_free[i] = T;

        // calculate the average enthalpy change
        double *num = (double *) malloc(size_S_conc*sizeof(int));
        double *den = (double *) malloc(size_S_conc*sizeof(int));

        // these are going to be arrays too. 
        double numerator   = 0.0;
        double denominator = 1.0;
        for (int j = 0; j < num_sites; j++){
            double bt = fit_beta_obj[j]*pow(T_conc_free[i],(j+1));

            numerator   += fit_dH_obj[j]*bt;
            denominator += bt;
        }

        int size_num_den = sizeof(numerator)/sizeof(int);
        double *avg_dH = (double *) malloc(size_num_den*sizeof(int));
        for (int j = 0; j < size_num_den; j++){
            avg_dH[j] = num[j]/den[j];
        }
        // = numerator/denominator;

        int size_avg_dH = sizeof(avg_dH)/sizeof(int);

        double *subset_first_dH = (double *) malloc((size_avg_dH - 1)*sizeof(int));
        for(int j = 1; j < size_avg_dH; j++){
            subset_first_dH[j] = avg_dH[j];
        }

        double *subset_last_dH = (double *) malloc((size_avg_dH - 1)*sizeof(int));
        for(int j = 0; j < size_avg_dH; j++){
            subset_last_dH[j] = avg_dH[j];
        }

        int size_x = size_avg_dH - 1;
        double *X = (double *) malloc(size_x*sizeof(int));
        for (int j = 0; j < size_x; j++){
            X[j] = subset_first_dH[j] - subset_last_dH[j];
        }
        // = subset_first_dH - subset_last_dH;

        double *subset_s_conc = (double *) malloc((num_shots - 1)*sizeof(int));
        for(int j = 1; j < num_shots; j++){
            subset_s_conc[j] = S_conc_corr[j];
        }

        float to_return = cell_volume**subset_s_conc**X + *dilution_heats;

        return to_return;

    }

}
