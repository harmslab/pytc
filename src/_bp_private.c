#include <Python.h>
#include <numpy/arrayobject.h>
#include "binding_polynomial.h"

static char module_docstring[] = 
    "calculate binding polynomial fit"

static char dQ_docstring[] = 
    "Calculate the heats that would be observed across shots for a given set
        of enthalpies and binding constants for each reaction.  This will work
        for an arbitrary-order binding polynomial."

static PyObject *bp_private_binding_polynomial(PyObject *self, PyObject *args)
{
    int num_sites;
    double fx_competent, cell_volume, dilution_heats;
    PyObject *fit_beta_obj, *fit_dH_obj, *S_conc_corr, *T_conc, *T_conc_free;

    if (!PyArg_ParseTuple(args, "dddi00000", &fx_competent, &cell_volume, &dilution_heats, &num_sites, 
                                        &fit_beta_obj, &fit_dH_obj, &S_conc_corr, &T_conc, &T_conc_free))
        return NULL;

    /* PyObjects to numpy arrays */
    PyObject *fit_beta_array = PyArray_FROM_OTF(fit_beta_obj, NPY_DOUBLE, NPY_IN_ARRAY);
    PyObject *fit_dH_array = PyArray_FROM_OTF(fit_dH_obj, NPY_DOUBLE, NPY_IN_ARRAY);
    PyObject *T_conc_array = PyArray_FROM_OTF(T_conc, NPY_DOUBLE, NPY_IN_ARRAY);
    PyObject *T_conc_free_array = PyArray_FROM_OTF(T_conc_free, NPY_DOUBLE, NPY_IN_ARRAY);
    PyObject *S_conc__corr_array = PyArray_FROM_OTF(S_conc_corr, NPY_DOUBLE, NPY_IN_ARRAY);

    /* throw exception if cast failed*/
    if (fit_beta_array == NULL || fit_dH_array == NULL || T_conc_array == NULL || 
            T_conc_free_array == NULL || S_conc_corr_array == NULL) {
        Py_XDECREF(fit_beta_array);
        Py_XDECREF(fit_dH_array);
        Py_XDECREF(T_conc_array);
        Py_XDECREF(T_conc_free_array);
        Py_XDECREF(S_conc_corr_array);
        return NULL;
    }

    /* pointers */
    double *fit_beta = (double*)PyArray_DATA(fit_beta_array);
    double *fit_dH = (double*)PyArray_DATA(fit_dH_array);
    double *T_conc_p = (double*)PyArray_DATA(T_conc_array);
    double *T_conc_free_p = (double*)PyArray_DATA(T_conc_free_array);
    double *S_conc_corr_p = (double*)PyArray_DATA(S_conc_array);

    /* get length of s_con_corr */
    int num_shots = (int)PyArray_DIM(S_conc_array, 0);

    /* call function */
    float value = dQ(fit_beta, fit_dH, S_conc_corr_p, T_conc_p, T_conc_free_p, cell_volume, 
                        dilution_heats, num_sites, num_shots, fx_competent);

    /* clean up */
    Py_DECREF(fit_beta_array);
    Py_DECREF(fit_dH_array);
    Py_DECREF(T_conc_array);
    Py_DECREF(T_conc_free_array);
    Py_DECREF(S_conc_corr_array);

    /* build output */
    PyObject *ret = Py_BuildValue("f", value);
    return ret;
}

static PyMethodDef module_methods[] = {
    {"dQ", bp_private_binding_polynomial, METH_VARARGS, dQ_docstring}
}

/* init function */
PyMODINIT_FUNC init_binding_polynomial(void)
{
    PyObject *m = Py_InitModule3("_bp_private", module_methods, module_docstring);
    if (m == NULL)
        return;
    /* Load numpy funcionality. */
    import_array();
}