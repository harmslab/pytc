double dQdT(double T_free, double S_total, double T_total, double *fit_beta_obj, int num_beta);

float dQ(double *fit_beta_obj, double *fit_dH_obj, double *S_conc_corr, double *T_conc, 
            double *T_conc_free, double cell_volume, double dilution_heats, 
            int num_sites, int num_shots, double fx_competent);