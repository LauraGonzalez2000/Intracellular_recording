import pandas as pd
import numpy as np
from scipy.stats import normaltest, levene, f_oneway, tukey_hsd, kruskal 
import scikit_posthocs as sp


import numpy as np
from scipy.stats import normaltest, levene

def test_parametric_conditions(values1, values2, values3): #FOR 3 GROUPS, not generalized
    """
    Tests if three groups meet parametric assumptions: normality and homoscedasticity.
    
    Parameters:
        values1, values2, values3 (array-like): Data samples for three groups.
    
    Returns:
        tuple: (normality, homoscedasticity, parametric) - Boolean flags for conditions.
    """
    
    normality = True
    homoscedasticity = True
    parametric = True

    # Test normality for all groups
    p_values = [normaltest(values)[1] for values in [values1, values2, values3]]

    if any(np.isnan(p) for p in p_values):
        normality = False
        print("Issue with normality check (NaN values detected).")
    
    if any(p < 0.05 for p in p_values):
        normality = False
        print("Data is not normally distributed.")

    # Test homoscedasticity (equal variances)
    statistic, p_value = levene(values1, values2, values3)

    if np.isnan(p_value):
        homoscedasticity = False
        print("Issue with homoscedasticity check (NaN value detected).")

    if p_value < 0.05:
        homoscedasticity = False
        print("Data does not have equal variances.")

    # Determine if parametric tests are suitable
    if not (normality and homoscedasticity):
        parametric = False
        print("Non-parametric tests should be used.")

    return normality, homoscedasticity, parametric

def calc_stats(title, values1, values2, values3, debug=False ):  #FOR 3 GROUPS, not generalized
        
        final_stats = np.array([[np.nan, np.nan, np.nan],
                                [np.nan, np.nan, np.nan],
                                [np.nan, np.nan, np.nan]])
        normality, homoscedasticity, parametric = test_parametric_conditions(values1, values2, values3)
        test1 = ''
        test2 = ''
        
        if parametric:
            # One way ANOVA test
            # null hypothesis : all groups are statistically similar
            print("Parametric test")
            test1 = 'ONE_WAY_ANOVA'
            F_stat, p_val = f_oneway(values1, 
                                     values2, 
                                     values3)  
            if (p_val < 0.05): #we can reject the null hypothesis, therefore there exists differences between groups
                #In order to differenciate groups, Tukey post hoc test    #could be Dunnett -> compare with control?
                test2='Tukey test'
                Tukey_result = tukey_hsd(values1, 
                                         values2, 
                                         values3)  
                final_stats = Tukey_result.pvalue

        else: 
            # Non parametric test : Kruskal Wallis test
            # Tests the null hypothesis that the population median of all of the groups are equal.
            print("Non parametric test")
            test1 = 'KRUSKAL_WALLIS'
            F_stat, p_val = kruskal(values1, 
                                    values2, 
                                    values3)
            
            if (p_val < 0.05):
                #we can reject the null hypothesis, therefore there exists differences between groups
                #In order to differenciate groups, Dunn's post hoc test
                test2='Dunn test, bonferroni adjust'
                data = {"Value":list(values1)+
                                list(values2)+
                                list(values3),
                        "Group":(["values_xe"] * len(list(values1)))+
                                (["values_kx"] * len(list(values2)))+
                                (["values_kxe"] * len(list(values3)))}
                df = pd.DataFrame(data)
                p_values = sp.posthoc_dunn(df, val_col="Value", group_col="Group", p_adjust='bonferroni')
                print(p_values)
                p_values_array = p_values.to_numpy()
                final_stats = p_values_array

        stats = {'Barplot':title,
                 'Normality': normality,
                 'Homescedasticity': homoscedasticity,
                 'Parametric': parametric,
                 'Test': test1,
                 'F_stat': F_stat,
                 'p_val': p_val, 
                 'Supplementary test':test2,
                 'final_stats':final_stats}
        
        if debug:
            print("stats\n", stats)
        return stats


if __name__=='__main__':
    print("statistics")
