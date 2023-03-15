#####################################################################################################
# PARETO was produced under the DOE Produced Water Application for Beneficial Reuse Environmental
# Impact and Treatment Optimization (PARETO), and is copyright (c) 2021 by the software owners: The
# Regents of the University of California, through Lawrence Berkeley National Laboratory, et al. All
# rights reserved.
#
# NOTICE. This Software was developed under funding from the U.S. Department of Energy and the
# U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted
# for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license
# in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform
# publicly and display publicly, and to permit other to do so.
#####################################################################################################
# Title: Supporting functions for both Operational and Strategic models

###############################################################################
### Imports
from pyomo.environ import (
    Param,
    value,
    Any,
)

# from pareto.strategic_water_management.strategic_produced_water_optimization import (
#    WaterQuality,
# )


###############################################################################
### Variable bounding manager functions
def UniversalVariableBounds(model):
    model = Bound_v_F_Piped(model)
    # TODO: Either implement number of trucks as data, or impute a bound from supply chain knowledge
    model = Bound_v_F_Trucked(
        model
    )  # THE USER MAY NEED TO UPDATE THE NUMBER OF TRUCKS MANUALLY
    return model


# =============================================================================
# def QualityMINLPVariableBounds(model):
#     model = Bound_v_Q_MINLP(model)
#     return model
# =============================================================================


def QualityPPVariableBounds(model):
    model = Bound_v_Q_PP(model)
    return model


def QualityDiscreteVariableBounds(model):
    model = Bound_v_F_DiscretePiped(model)
    return model


###############################################################################
### Individual variable bound generation functions

# =============================================================================
# # Max Bounds - uses largest pipeline capacity + maximum expansion
# def Bound_v_F_Piped(model):
#     # Set up bounds in a parameter
#     model.p_F_Piped_UB = Param(
#         model.s_L,
#         model.s_L,
#         default = # set default value to maximum capacity plus maximum expansion capacity
#         max([value(model.p_sigma_Pipeline[l,l_tilde]) for (l,l_tilde) in model.s_LLA]) +
#         max([value(model.p_delta_Pipeline[d]) for d in model.s_D]),
#         mutable=True,
#         units=model.model_units["volume_time"],
#         doc="Maximum pipeline capacity between nodes [volume_time]",
#     )
#     # Assign upper bounds to variables; note that using a bounds rule would require redefining the variable
#     for key in model.s_LLA:
#         for t in model.s_T:
#             model.v_F_Piped[key,t].setub(model.p_F_Piped_UB[key])
#     return model
# =============================================================================
# Tight Bounds - uses pipeline capacity by location + maximum expansion
def Bound_v_F_Piped(model):
    # initialization function for parameter
    def p_F_Piped_UB_init(model, l, l_tilde):
        # set default value to pieline capacity plus maximum expansion capacity
        return model.p_sigma_Pipeline[l, l_tilde] + max(
            [value(model.p_delta_Pipeline[d]) for d in model.s_D]
        )

    # Set up bounds in a parameter
    model.p_F_Piped_UB = Param(
        model.s_L,
        model.s_L,
        default=None,
        mutable=True,
        initialize=p_F_Piped_UB_init,
        units=model.model_units["volume_time"],
        doc="Maximum pipeline capacity between nodes [volume_time]",
    )
    # Assign upper bounds to variables; note that using a bounds rule would require redefining the variable
    for key in model.s_LLA:
        for t in model.s_T:
            model.v_F_Piped[key, t].setub(model.p_F_Piped_UB[key])
    return model


def Bound_v_F_Trucked(model):
    # create a parameter for truck maximum capacity - WILL NEED A PROPER VALUE LATER!!!
    model.p_max_trucking = Param(
        initialize=1000
        * model.p_delta_Truck,  # NOTE: MODEL IS SENSITIVE TO THIS PARAMETER - LOOSER IS WORSE
        doc="Upperbound on v_F_Trucked, assumes there are as many trucks as indicated available on all routes",
        units=model.model_units["volume_time"],
    )
    # Assign upper bounds to variables
    for key in model.s_LLT:
        for t in model.s_T:
            model.v_F_Trucked[key, t].setub(model.p_max_trucking)
    return model


# =============================================================================
# def Bound_v_Q_MINLP(model):
#     """
#     Variable bounding function for water quality variable v_Q in the MINLP
#     strategic water quality extension
#
#     Notes on contents:
#         - uses the maximum value among several parameters at each node as bound
#         - not all parameters will be defined on every index
#         - "None" is a valid entry for a pyomo variable bound, meaning no bound
#         - function "TryOrNone()" is used to return None if a parameter is not
#           defined on a given index
#         - If no parameter is defined at an index, then use None as that bound
#     """
#     # initilization function for model.quality.p_Q_UB
#     def p_Q_UB_init(model,l,w):
#         vals = []
#         vals.append(TryOrNone(model.quality.p_xi_StorageSite, (l,w)))
#         vals.append(TryOrNone(model.quality.p_xi_PadStorage, (l,w)))
#         vals.append(TryOrNone(model.quality.p_nu_pad, (l,w)))
#         vals.append(TryOrNone(model.quality.p_nu_freshwater, (l,w)))
#         try:
#             val = max(val for val in vals if val != None)
#         except:
#             val = None
#         finally:
#             return val
#     # Create a parameter with maximum quality values
#     model.quality.p_Q_UB = Param(
#         model.quality.s_WQL,
#         model.quality.s_QC,
#         within=Any,
#         default=None,
#         mutable=True,
#         initialize=p_Q_UB_init,
#         units=model.model_units["concentration"],
#     )
#     # Assign upper bounds to variables
#     for l in model.quality.s_WQL:
#         for w in model.quality.s_QC:
#             for t in model.s_T:
#                 model.quality.v_Q[l,w,t].setub(model.quality.p_Q_UB[l,w])
#     return model
# =============================================================================


def Bound_v_Q_PP(model):
    """
    Variable bounding function for water quality variable v_Q in the post
    processing strategic water quality extension

    Notes on contents:
        - uses the maximum value among several parameters at each node as bound
        - not all parameters will be defined on every index
        - "None" is a valid entry for a pyomo variable bound, meaning no bound
        - function "TryOrNone()" is used to return None if a parameter is not
          defined on a given index
        - If no parameter is defined at an index, then use None as that bound
    """
    # =============================================================================
    #     # initilization function for model.quality.p_Q_UB
    #     def p_Q_UB_init(model, l, w):
    #         vals = []
    #         vals.append(TryOrNone(model.p_xi_StorageSite, (l, w)))
    #         vals.append(TryOrNone(model.p_xi_PadStorage, (l, w)))
    #         vals.append(TryOrNone(model.p_nu_pad, (l, w)))
    #         vals.append(TryOrNone(model.p_nu_freshwater, (l, w)))
    #         try:
    #             val = max(val for val in vals if val != None)
    #         except:
    #             val = None
    #         finally:
    #             return val
    # =============================================================================

    quality_highest_bound = max(
        max([x.value for x in model.quality.p_xi_StorageSite.values()]),
        max([x.value for x in model.quality.p_xi_PadStorage.values()]),
        max([x.value for x in model.quality.p_nu_pad.values()]),
        max([x.value for x in model.quality.p_nu_freshwater.values()]),
    )

    # Create a parameter with maximum quality values
    model.quality.p_Q_UB = Param(
        model.quality.s_WQL,
        model.s_QC,
        within=Any,
        default=None,
        mutable=True,
        # initialize=p_Q_UB_init,
        units=model.model_units["concentration"],
    )
    # Assign upper bounds to variables
    for l in model.quality.s_WQL:
        for w in model.s_QC:
            for t in model.s_T:
                # Individual quality bounds (NOTE: HAVE SHOWN, THIS DOES NOT WORK)
                # model.quality.v_Q[l, w, t].setub(model.quality.p_Q_UB[l, w])
                # Highest single quality bound
                model.quality.v_Q[l, w, t].setub(quality_highest_bound)
    return model


def TryOrNone(par, ind):
    """
    A helper function that checks if a parameter is defined on an index,
    returning the parameter value if it is, and None if it is not
    """
    try:
        val = value(par[ind])
    except:
        val = None
    finally:
        return val


# Quality parameters and their indices
# model.quality.p_xi_StorageSite[s_S, s_WT]
# model.quality.p_xi_PadStorage[s_CP, s_WT]
# model.quality.p_nu_pad[s_P, s_WT]
# model.quality.p_nu_freshwater[s_F, s_WT]


def Bound_v_F_DiscretePiped(model):
    # initialization function for parameter
    def p_F_DiscretePiped_UB_init(model, l, l_tilde):
        # set default value to pieline capacity plus maximum expansion capacity
        return model.p_sigma_Pipeline[l, l_tilde] + max(
            [value(model.p_delta_Pipeline[d]) for d in model.s_D]
        )

    # Set up bounds in a parameter
    model.p_F_DiscretePiped_UB = Param(
        model.s_L,
        model.s_L,
        default=None,
        mutable=True,
        initialize=p_F_DiscretePiped_UB_init,
        units=model.model_units["volume_time"],
        doc="Maximum pipeline capacity between nodes [volume_time]",
    )
    # Assign upper bounds to variables
    for key in model.s_NonPLP:
        for t in model.s_T:
            for w in model.s_QC:
                for q in model.s_Q:
                    model.v_F_DiscretePiped[key, t, w, q].setub(
                        model.p_F_DiscretePiped_UB[key]
                    )
    return model