
import pytc
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

#goldberg et al (2002) Journal of Physical and Chemical Reference Data 31 231,  doi: 10.1063/1.1416902
hepes_ionization_dH = 20.4/4.184*1000
imid_ionization_dH = 36.64/4.184*1000
tris_ionization_dH = 47.45/4.184*1000

g = pytc.ProtonLinked()

hepes1 = pytc.ITCExperiment("ca-edta-expt/HEPES/CaEDTAHEPES03_area.DH",pytc.models.SingleSite,shot_start=2)
hepes2 = pytc.ITCExperiment("ca-edta-expt/HEPES/CaEDTAHEPES05_area.DH",pytc.models.SingleSite,shot_start=2)
hepes3 = pytc.ITCExperiment("ca-edta-expt/HEPES/CaEDTAHEPES06_area.DH",pytc.models.SingleSite,shot_start=2)
hepes4 = pytc.ITCExperiment("ca-edta-expt/HEPES/CaEDTAHEPES07_area.DH",pytc.models.SingleSite,shot_start=2)
#hepes5 = pytc.ITCExperiment("ca-edta-expt/HEPES/CaHEPESBlank_out.DH",pytc.models.Blank,shot_start=2)

tris1 = pytc.ITCExperiment("ca-edta-expt/Tris/CaEDTATris05_area.DH",pytc.models.SingleSite,shot_start=2)
tris2 = pytc.ITCExperiment("ca-edta-expt/Tris/CaEDTATris06_area.DH",pytc.models.SingleSite,shot_start=2)
tris3 = pytc.ITCExperiment("ca-edta-expt/Tris/CaEDTATris07_area.DH",pytc.models.SingleSite,shot_start=2)
#tris4 = pytc.ITCExperiment("ca-edta-expt/Tris/CaTrisBlank.DH",pytc.models.Blank,shot_start=2)

imid1 = pytc.ITCExperiment("ca-edta-expt/Imidazole/CaEDTAImid04_area.DH",pytc.models.SingleSite,shot_start=2)
imid3 = pytc.ITCExperiment("ca-edta-expt/Imidazole/CaEDTAImid06_area.DH",pytc.models.SingleSite,shot_start=2)
imid4 = pytc.ITCExperiment("ca-edta-expt/Imidazole/CaEDTAImid08_area.DH",pytc.models.SingleSite,shot_start=2)
imid5 = pytc.ITCExperiment("ca-edta-expt/Imidazole/CaEDTAImid09_area.DH",pytc.models.SingleSite,shot_start=2)
#imid6 = pytc.ITCExperiment("ca-edta-expt/Imidazole/CaImidBlank_out.DH",pytc.models.Blank,shot_start=2)

g.add_experiment(hepes1,ionization_enthalpy=hepes_ionization_dH)
g.add_experiment(hepes2,ionization_enthalpy=hepes_ionization_dH)  
g.add_experiment(hepes3,ionization_enthalpy=hepes_ionization_dH)
g.add_experiment(hepes4,ionization_enthalpy=hepes_ionization_dH)
#g.add_experiment(hepes5,ionization_enthalpy=hepes_ionization_dH)

g.add_experiment(tris1,ionization_enthalpy=tris_ionization_dH)
g.add_experiment(tris2,ionization_enthalpy=tris_ionization_dH)  
g.add_experiment(tris3,ionization_enthalpy=tris_ionization_dH)
#g.add_experiment(tris4,ionization_enthalpy=tris_ionization_dH)

g.add_experiment(imid1,ionization_enthalpy=imid_ionization_dH)
g.add_experiment(imid3,ionization_enthalpy=imid_ionization_dH)
g.add_experiment(imid4,ionization_enthalpy=imid_ionization_dH)
g.add_experiment(imid5,ionization_enthalpy=imid_ionization_dH)
#g.add_experiment(imid6,ionization_enthalpy=imid_ionization_dH)


g.link_to_global(hepes1,"K","global_K")
g.link_to_global(hepes2,"K","global_K")
g.link_to_global(hepes3,"K","global_K")
g.link_to_global(hepes4,"K","global_K")

g.link_to_global(tris1,"K","global_K")
g.link_to_global(tris2,"K","global_K")
g.link_to_global(tris3,"K","global_K")

g.link_to_global(imid1,"K","global_K")
g.link_to_global(imid3,"K","global_K")
g.link_to_global(imid4,"K","global_K")
g.link_to_global(imid5,"K","global_K")

g.link_to_global(hepes1,"dH","dH_global")
g.link_to_global(hepes2,"dH","dH_global")
g.link_to_global(hepes3,"dH","dH_global")
g.link_to_global(hepes4,"dH","dH_global")

g.link_to_global(tris1,"dH","dH_global")
g.link_to_global(tris2,"dH","dH_global")
g.link_to_global(tris3,"dH","dH_global")

g.link_to_global(imid1,"dH","dH_global")
g.link_to_global(imid3,"dH","dH_global")
g.link_to_global(imid4,"dH","dH_global")
g.link_to_global(imid5,"dH","dH_global")

"""
g.link_to_global(hepes1,"dilution_heat","hepes_heat")
g.link_to_global(hepes2,"dilution_heat","hepes_heat")
g.link_to_global(hepes3,"dilution_heat","hepes_heat")
g.link_to_global(hepes4,"dilution_heat","hepes_heat")
g.link_to_global(hepes5,"dilution_heat","hepes_heat")

g.link_to_global(tris1,"dilution_heat","tris_heat")
g.link_to_global(tris2,"dilution_heat","tris_heat")
g.link_to_global(tris3,"dilution_heat","tris_heat")
g.link_to_global(tris4,"dilution_heat","tris_heat")

g.link_to_global(imid1,"dilution_heat","imid_heat")
g.link_to_global(imid3,"dilution_heat","imid_heat")
g.link_to_global(imid4,"dilution_heat","imid_heat")
g.link_to_global(imid5,"dilution_heat","imid_heat")
g.link_to_global(imid6,"dilution_heat","imid_heat")

g.link_to_global(hepes1,"dilution_intercept","hepes_intercept")
g.link_to_global(hepes2,"dilution_intercept","hepes_intercept")
g.link_to_global(hepes3,"dilution_intercept","hepes_intercept")
g.link_to_global(hepes4,"dilution_intercept","hepes_intercept")
g.link_to_global(hepes5,"dilution_intercept","hepes_intercept")

g.link_to_global(tris1,"dilution_intercept","tris_intercept")
g.link_to_global(tris2,"dilution_intercept","tris_intercept")
g.link_to_global(tris3,"dilution_intercept","tris_intercept")
g.link_to_global(tris4,"dilution_intercept","tris_intercept")

g.link_to_global(imid1,"dilution_intercept","imid_intercept")
g.link_to_global(imid3,"dilution_intercept","imid_intercept")
g.link_to_global(imid4,"dilution_intercept","imid_intercept")
g.link_to_global(imid5,"dilution_intercept","imid_intercept")
g.link_to_global(imid6,"dilution_intercept","imid_intercept")
"""

g.update_bounds("global_K",(1,np.inf))
g.update_bounds("num_protons",(-5.0,5.0))


g.fit()

pp = PdfPages('test-proton.pdf')
g.plot(correct_molar_ratio=True) #,subtract_dilution=True) #,correct_molar_ratio=True)
plt.savefig(pp, format='pdf')
pp.close()
        
for k in g.fit_param[0].keys():
    print("global",k,g.fit_param[0][k],g.fit_error[0][k])
    
for i in range(len(g.fit_param[1])):
    for k in g.fit_param[1][i].keys():
        print("local",i,k,g.fit_param[1][i][k],g.fit_error[1][i][k])
