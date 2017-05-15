#include "binding_polynomial.h"
#include <math.h>
#define MIN(a, b) ((a) < (b) ? (a) : (b))

double dQdT(double *T_free, double *S_total, double *T_total, double *fit_beta_obj, int num_beta){
    /*
    T_total = T_free + S_total*(dln(P)/dln(T_free)), so:
        0 = T_free + S_total*(dln(P)/dln(T_free)) - T_total

        Solve this for T_free to find free titrant.

        dln(P)/dln(T_free)

        P = (beta1*T_free**1) *  b2*T**2 
    */
    int i;
    double numerator, denominator;

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

float dQ(double *fit_beta_obj, double *fit_dH_obj, double *S_conc_corr, double *T_conc, 
            double *T_conc_free, double cell_volume, double dilution_heats, 
            int num_sites, int num_shots, double fx_competent){

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
                    T_conc_free[i] = self._T_conc[i];

                // root is closest to min --> set to that
                } else {
                    T_conc_free[i] = 0.0;
                }
            }
            continue;
        }
        
        double args[2] = {S_conc_corr[i], T_conc[i]};
        double T = brentq(dQdT, 0 , T_conc[-1], args);

        // numerical problems sometimes make T slightly bigger than the total
        // concentration, so bring down to the correct value
        if (T > T_conc[i]) { T = T_conc[i]; }
        T_conc_free[i] = T;

        // calculate the average enthalpy change
        double numerator   = 0.0;
        double denominator = 1.0;
        for (int j = 0; j < num_sites; j++){
            double bt = fit_beta_obj[j]*pow(T_conc_free[i],(j+1));
            numerator   += fit_dH_obj[j]*bt;
            denominator += bt;
        }

        double avg_dH = numerator/denominator;

        float X = avg_dH[1:] - avg_dH[:-1];

        float to_return = cell_volume*S_conc_corr[1:]*X + dilution_heats;

        return to_return;

    }

}
