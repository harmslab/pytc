
from . import OriginExperiment, NitpicExperiment

def ITCExperiment(dh_file,model,shot_start=1,units="cal/mol",uncertainty=0.1,
                  **model_kwargs):
    """
    Wrapper that creates a BaseITCExperiment instance that that holds an ITC
    experiment and the model that describes it.  It looks at "dh_file" and 
    decides which kind of parser to use. 

    Parameters
    ----------

    dh_file: string
        integrated heats file written out by origin software.
    model: ITCModel subclass instance
        ITCModel subclass to use for modeling
    shot_start: int
        what shot to use as the first real point.  Shots start at 0, so
        default=1 discards first point.
    units : string
        file units ("cal/mol","kcal/mol","J/mol","kJ/mol") 
    uncertainty : float > 0.0
        uncertainty in integrated heats (set to same for all shots, unless
        specified in something like NITPIC output file). 
 
    **model_kwargs: any keyword arguments to pass to the model.  Any
                    keywords passed here will override whatever is
                    stored in the dh_file.
    """

    extension = dh_file.split(".")[-1].lower()

    if extension == "dh":
        return OriginExperiment(dh_file,model,shot_start,units,uncertainty,
                                **model_kwargs)
    elif extension == "sedphat":
        return NitpicExperiment(dh_file,model,shot_start,units,uncertainty,
                                **model_kwargs)
    else:
        err = "dh_file type could not be determined.\n"
        raise ValueError(err)

