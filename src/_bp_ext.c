#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

/*-----------------------------------------------------------------------------
 * Binding polynomial bit
 * --------------------------------------------------------------------------*/

#define MIN(a, b) ((a) < (b) ? (a) : (b))

typedef struct {

    double S_total, T_total;
    double *fit_beta_array;
    int num_beta;

} dqdt_args;

typedef double (*callback_type)(double,dqdt_args *);

double dQdT(double T_free, dqdt_args *args){
    /*
    T_total = T_free + S_total*(dln(P)/dln(T_free)), so:
        0 = T_free + S_total*(dln(P)/dln(T_free)) - T_total

        Solve this for T_free to find free titrant.

        dln(P)/dln(T_free)

        P = (beta1*T_free**1) *  b2*T**2 
    */
    int i;
    double numerator, denominator, bt, P;

    numerator = 0;
    denominator = 1;

    for (i = 0; i < args->num_beta; i++){
        bt = args->fit_beta_array[i]*pow(T_free,(i+1)); 
        numerator   += (i+1)*bt;
        denominator +=       bt;
    }

    P = numerator/denominator;

    return T_free + args->S_total*P - args->T_total;

}

double brent_func(callback_type f, double xa, double xb, dqdt_args *args) {

    double xpre = xa, xcur = xb;
    double xblk = 0., fpre, fcur, fblk = 0., spre = 0., scur = 0., sbis;
    double xtol = 2e-12;
    // 4*finfo(float).eps
    double rtol = 8.8817841970012523e-16;
    // the tolerance is 2*delta
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
                // interpolate
                stry = -fcur*(xcur - xpre)/(fcur - fpre);
            }
            else {
                // extrapolate
                dpre = (fpre - fcur)/(xpre - xcur);
                dblk = (fblk - fcur)/(xblk - xcur);
                stry = -fcur*(fblk*dblk - fpre*dpre)
                    /(dblk*dpre*(fblk - fpre));
            }
            if (2*fabs(stry) < MIN(fabs(spre), 3*fabs(sbis) - delta)) {
                // good short step
                spre = scur;
                scur = stry;
            } else {
                // bisect
                spre = sbis;
                scur = sbis;
            }
        }
        else {
            // bisect 
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

void *dQ(double *fit_beta_obj, double *fit_dH_obj, double *S_conc_corr, double *T_conc, 
            double *T_conc_free, double cell_volume, double *dilution_heats, int num_sites, 
            int num_shots, int size_T_conc, double *final_array){

    double min_value, max_value, bt, T;
    int i, j, lastT;
    int num_shots_reduced = num_shots - 1;
    float DELTA = 0.0, TOLERANCE = 1e-12;
    double *numerator, *denominator, *avg_dH, *subset_first_dH, *subset_last_dH, *X, *subset_s_conc;

    dqdt_args args;
    args.S_total = 0.0;
    args.T_total = 0.0;
    args.fit_beta_array = fit_beta_obj;
    args.num_beta = num_sites;

    // num and denom arrays
    numerator = (double *)malloc(num_shots*sizeof(double));
    if (numerator== NULL){
        return NULL;
    }
    for (i = 0; i < num_shots; i++){
        numerator[i] = 0.0;
    }
    denominator = (double *)malloc(num_shots*sizeof(double));
    if (denominator == NULL){
        return NULL;
    }

    for (i = 0; i < num_shots; i++){
        denominator[i] = 1.0;
    }
    
    for (i = 0; i < num_shots; i++){

        if (fabs(T_conc[i] - DELTA) < TOLERANCE){
            T_conc_free[i] = 0.0;
            continue;
        }
        args.S_total = S_conc_corr[i];
        args.T_total = T_conc[i];

        min_value = dQdT(0.0,&args);
        max_value = dQdT(T_conc[i],&args);
            
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

        //double args[2] = {S_conc_corr[i], T_conc[i]};
        lastT = size_T_conc - 1;
        T = brent_func(dQdT, 0 , T_conc[lastT], &args);

        // numerical problems sometimes make T slightly bigger than the total
        // concentration, so bring down to the correct value
        if (T > T_conc[i]) { T = T_conc[i]; }
        T_conc_free[i] = T;
    }

    // calculate the average enthalpy change
    for (i = 0; i < num_sites; i++){
        for(j = 0; j < num_shots; j++){
            bt = fit_beta_obj[i]*pow(T_conc_free[j],(i+1));
            numerator[j] += fit_dH_obj[i]*bt;
            denominator[j] += bt;
        }
    }

    avg_dH = (double *)malloc(num_shots*sizeof(double));
    if (avg_dH == NULL){
        return NULL;
    }

    for (i = 0; i < num_shots; i++){
        avg_dH[i] = numerator[i]/denominator[i];
    }
    // avg_dh[1:]
    subset_first_dH = (double *)malloc(num_shots_reduced*sizeof(double));
    if (subset_first_dH == NULL){
        return NULL;
    }
    for(i = 0; i < num_shots_reduced; i++){
        subset_first_dH[i] = avg_dH[i+1];
    }

    // avg_dh[:-1]
    subset_last_dH = (double *)malloc(num_shots_reduced*sizeof(double));
    if (subset_last_dH == NULL){
        return NULL;
    }
    for(i = 0; i < num_shots_reduced; i++){
        subset_last_dH[i] = avg_dH[i];
    }

    // avg_dh[1:]-avg_dh[:-1];
    X = (double *)malloc(num_shots_reduced*sizeof(double));
    if (X == NULL){
        return NULL;
    }
    for (i = 0; i < num_shots_reduced; i++){
        X[i] = subset_first_dH[i] - subset_last_dH[i];
    }

    // S_conc_corr[1:]
    subset_s_conc = (double *)malloc(num_shots_reduced*sizeof(double));
    if (subset_s_conc == NULL){
        return NULL;
    }
    for(i = 0; i < num_shots_reduced; i++){
        subset_s_conc[i] = S_conc_corr[i+1];
    }

    for(i = 0; i < num_shots_reduced; i++){
        final_array[i] = cell_volume*subset_s_conc[i]*X[i] + dilution_heats[i];
    }

    // clean up
    // free memory
    free(avg_dH);
    free(subset_first_dH);
    free(subset_last_dH);
    free(X);
    free(subset_s_conc);
    free(numerator);
    free(denominator);

    return NULL;
}

/*-----------------------------------------------------------------------------
 * Extension bit
 * --------------------------------------------------------------------------*/

// docstrings
static char module_docstring[] = 
    "calculate binding polynomial fit";

static char dQ_docstring[] = 
    "Calculate the heats that would be observed across shots for a given set of enthalpies and binding constants for each reaction. This will work for an arbitrary-order binding polynomial.";

static PyObject *bp_ext_dQ(PyObject *self, PyObject *args);

// methods
static PyMethodDef module_methods[] = {
    {"dQ", bp_ext_dQ, METH_VARARGS, dQ_docstring},
    {NULL, NULL}
};

// init function
PyMODINIT_FUNC PyInit_bp_ext(void)
{
    PyObject *module;
    static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "bp_ext",
        module_docstring,
        -1,
        module_methods,
        NULL,
        NULL,
        NULL,
        NULL
    };

    module = PyModule_Create(&moduledef);
    if (!module) return NULL;

    // Load numpy funcionality.
    import_array();

    return module;
}

static PyObject *bp_ext_dQ(PyObject *self, PyObject *args)
{   
    int num_sites, num_shots, size_T_conc;
    double cell_volume;
    PyObject *fit_beta_obj, *fit_dH_obj, *S_conc_corr, *T_conc, *T_conc_free, *dilution_heats, *final_array;

    if (!PyArg_ParseTuple(args, "diiiOOOOOOO:dQ", &cell_volume, &num_shots, &size_T_conc, &num_sites, 
                                        &dilution_heats, &fit_beta_obj, &fit_dH_obj, &S_conc_corr, &T_conc, 
                                        &T_conc_free, &final_array)){
        return NULL;
    }

    // PyObjects to numpy arrays
    PyObject *fit_beta_array = PyArray_FROM_OTF(fit_beta_obj, NPY_DOUBLE, NPY_IN_ARRAY);
    PyObject *fit_dH_array = PyArray_FROM_OTF(fit_dH_obj, NPY_DOUBLE, NPY_IN_ARRAY);
    PyObject *T_conc_array = PyArray_FROM_OTF(T_conc, NPY_DOUBLE, NPY_IN_ARRAY);
    PyObject *T_conc_free_array = PyArray_FROM_OTF(T_conc_free, NPY_DOUBLE, NPY_IN_ARRAY);
    PyObject *S_conc_corr_array = PyArray_FROM_OTF(S_conc_corr, NPY_DOUBLE, NPY_IN_ARRAY);
    PyObject *dilution_heats_array = PyArray_FROM_OTF(dilution_heats, NPY_DOUBLE, NPY_IN_ARRAY);
    PyObject *final_array_obj = PyArray_FROM_OTF(final_array, NPY_DOUBLE, NPY_IN_ARRAY);

    // throw exception if cast failed
    if (fit_beta_array == NULL || fit_dH_array == NULL || T_conc_array == NULL || T_conc_free_array == NULL || 
        S_conc_corr_array == NULL || dilution_heats_array == NULL || final_array_obj == NULL) {
        Py_XDECREF(fit_beta_array);
        Py_XDECREF(fit_dH_array);
        Py_XDECREF(T_conc_array);
        Py_XDECREF(T_conc_free_array);
        Py_XDECREF(S_conc_corr_array);
        Py_XDECREF(dilution_heats_array);
        Py_XDECREF(final_array_obj);
        return NULL;
    }

    // pointers 
    double *fit_beta = (double*)PyArray_DATA(fit_beta_array);
    double *fit_dH = (double*)PyArray_DATA(fit_dH_array);
    double *T_conc_p = (double*)PyArray_DATA(T_conc_array);
    double *T_conc_free_p = (double*)PyArray_DATA(T_conc_free_array);
    double *S_conc_corr_p = (double*)PyArray_DATA(S_conc_corr_array);
    double *dilution_heats_p = (double*)PyArray_DATA(dilution_heats_array);
    double *final_array_p = (double*)PyArray_DATA(final_array_obj);

    // call function 
    dQ(fit_beta, fit_dH, S_conc_corr_p, T_conc_p, T_conc_free_p, cell_volume, dilution_heats_p, 
        num_sites, num_shots, size_T_conc, final_array_p);

    // clean up 
    Py_DECREF(fit_beta_array);
    Py_DECREF(fit_dH_array);
    Py_DECREF(T_conc_array);
    Py_DECREF(T_conc_free_array);
    Py_DECREF(S_conc_corr_array);
    Py_DECREF(dilution_heats_array);

    // check errors
    /*if (value == NULL){
        PyErr_SetString(PyExc_RuntimeError, "object return null");

        return NULL;
    }*/

    // build output and return
    return Py_BuildValue("O", final_array_obj);
}
