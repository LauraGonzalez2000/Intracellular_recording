import pandas as pd
import numpy as np
from scipy.stats import f_oneway, tukey_hsd, normaltest, kruskal, levene
import scikit_posthocs as sp


def test_parametric_conditions(self, values1, values2, values3):
        norm = True
        homes = True
        parametric=True
        #test conditions to apply statistical test:
            
        #test normality (The three groups are normally distributed): 
        stat1, p_val1 = normaltest(values1)
        stat2, p_val2 = normaltest(values2)
        stat3, p_val3 = normaltest(values3)
        if (np.isnan(p_val1)):
            norm=False
            print("issue with normality check")
        if (np.isnan(p_val2)):
            norm=False
            print("issue with normality check")
        if (np.isnan(p_val3)):
            norm=False
            print("issue with normality check")
        if (p_val1< 0.05):
            norm=False
            print("data is not normally distributed")
        if (p_val2< 0.05): 
            norm=False
            print("data is not normally distributed")
        if (p_val3< 0.05):
            norm=False
            print("data is not normally distributed")

            
        #test homoscedasticity (The three groups have a homogeneity of variance; meaning the population variances are equal):
        #The Levene test tests the null hypothesis that all input samples are from populations with equal variances.
        statistic, p_value = levene(values1, 
                                    values2, 
                                    values3)
        if (np.isnan(p_value)):
            norm=False
            print("issue with homoscedasticity check")
        if (p_value <0.05):
            #null hypothesis is rejected, the population variances are not equal!
            homes=False
            print("data does not have equal variances")

        if (norm==False): 
            parametric=False
            print("non parametric tests should be used")

        if (homes==False):
            parametric=False
            print("non parametric tests should be used")

        return norm, homes, parametric

def calc_stats(self, metric, IGOR_results_df, debug=False ):
        final_stats = np.array([[np.nan, np.nan, np.nan],
                                [np.nan, np.nan, np.nan],
                                [np.nan, np.nan, np.nan]])
        #statistic performed within a specific group:
        values_xe = IGOR_results_df.loc[IGOR_results_df['Group']=='xyla euthasol',  metric].values
        values_kx = IGOR_results_df.loc[IGOR_results_df['Group']=='ketaxyla',  metric].values
        values_kxe = IGOR_results_df.loc[IGOR_results_df['Group']=='keta xyla euthasol',  metric].values

        norm, homes, parametric = self.test_parametric_conditions(values_xe, values_kx, values_kxe)
        test2 = ""
        # One way ANOVA test
        # null hypothesis : all groups are statistically similar
        if parametric:
            print("Parametric test")
            test = 'ONE_WAY_ANOVA'
            F_stat, p_val = f_oneway(values_xe, 
                                     values_kx, 
                                     values_kxe )  
            if (p_val < 0.05): #we can reject the null hypothesis, therefore there exists differences between groups
                #In order to differenciate groups, Tukey post hoc test    #could be Dunnett -> compare with control?
                test2='Tukey test'
                Tukey_result = tukey_hsd(values_xe, 
                                         values_kx, 
                                         values_kxe )  
                final_stats = Tukey_result.pvalue

        # Non parametric test : Kruskal Wallis test
        # Tests the null hypothesis that the population median of all of the groups are equal.
        else: 
            print("Non parametric test")
            test = 'KRUSKAL_WALLIS'
            F_stat, p_val = kruskal(values_xe, 
                                    values_kx, 
                                    values_kxe)
            
            if (p_val < 0.05):
                test2='Dunn test, bonferroni adjust'
                #we can reject the null hypothesis, therefore there exists differences between groups
                #In order to differenciate groups, Dunn's post hoc test
                data = {"Value":list(values_xe)+
                                list(values_kx)+
                                list(values_kxe),
                        "Group":(["values_xe"] * len(list(values_xe)))+
                                (["values_kx"] * len(list(values_kx)))+
                                (["values_kxe"] * len(list(values_kxe)))}
                df = pd.DataFrame(data)
                p_values = sp.posthoc_dunn(df, val_col="Value", group_col="Group", p_adjust='bonferroni')
                p_values_array = p_values.to_numpy()
                final_stats = p_values_array

        stats = {'Barplot':metric,
                 'Normality': norm,
                 'Homescedasticity': homes,
                 'Parametric': parametric,
                 'Test': test,
                 'F_stat': F_stat,
                 'p_val': p_val, 
                 'Supplementary test':test2,
                 'final_stats':final_stats}
        
        if debug:
            print("stats\n", stats)
            
        return stats
  




###### MAIN ######################################################

if __name__=='__main__':
    print("statistics")