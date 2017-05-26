typedef struct {

    double S_total, T_total;
    double *fit_beta_array;
    int num_beta;

} dqdt_args;

typedef double (*callback_type)(double,dqdt_args *);

double dQdT(double T_free, dqdt_args *args);

void *dQ(double *fit_beta_obj, double *fit_dH_obj, double *S_conc_corr, double *T_conc, 
            double *T_conc_free, double cell_volume, double *dilution_heats, int num_sites, 
            int num_shots, int size_T_conc, double *final_array);

double brent_func(callback_type f, double xa, double xb, dqdt_args *args);