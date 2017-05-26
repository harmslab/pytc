#include <Python.h>
//#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include "binding_polynomial.h"
#include <stdio.h>

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
