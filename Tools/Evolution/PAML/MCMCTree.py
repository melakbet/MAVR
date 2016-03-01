#!/usr/bin/env python
__author__ = 'Sergei F. Kliver'

from Tools.Abstract import Tool


class MCMCTree(Tool):
    def __init__(self, path="", max_threads=4):
        Tool.__init__(self, "mcmctree", path=path, max_threads=max_threads)
        self.example = """
          seed = -1
       seqfile = mtCDNApri123.txt
      treefile = mtCDNApri.trees
       outfile = out

         ndata = 3
       seqtype = 0    * 0: nucleotides; 1:codons; 2:AAs
       usedata = 1    * 0: no data; 1:seq like; 2:normal approximation; 3:out.BV (in.BV)
         clock = 2    * 1: global clock; 2: independent rates; 3: correlated rates
       RootAge = '<1.0'  * safe constraint on root age, used if no fossil for root.

         model = 0    * 0:JC69, 1:K80, 2:F81, 3:F84, 4:HKY85
         alpha = 0    * alpha for gamma rates at sites
         ncatG = 5    * No. categories in discrete gamma

     cleandata = 0    * remove sites with ambiguity data (1:yes, 0:no)?

       BDparas = 1 1 0.1   * birth, death, sampling
   kappa_gamma = 6 2      * gamma prior for kappa
   alpha_gamma = 1 1      * gamma prior for alpha

   rgene_gamma = 2 20    * gammaDir prior for rate for genes
  sigma2_gamma = 1 10   * gammaDir prior for sigma^2     (for clock=2 or 3)

      finetune = 1: .1 .1 .1 .1 .1 .1 * auto (0 or 1): times, musigma2, rates, mixing, paras, FossilErr

         print = 1
        burnin = 2000
      sampfreq = 2
       nsample = 20000
        """

    def write_example_ctl(self, example_file):
        with open(example_file, "w") as example_fd:
            example_fd.write(self.example)

    def print_example_ctl(self):
        print(self.example)


    @staticmethod
    def generate_ctl_file(seq_file, tree_file, out_file, ctl_file, seed=-1, num_of_partitions=1,
                          seq_type="nucleotides", use_data=1, clock="global", root_age=None,
                          model="HKY85", ncatG=5, alpha_for_gamma_rates_at_sites=0.5,
                          birth=1.0, death=1.0, sampling=0.1,
                          alpha_gamma_alpha=1.0, alpha_gamma_beta=1.0, kappa_gamma_alpha=6.0, kappa_gamma_beta=2.0,
                          rgene_gamma_alpha=2.0, rgene_gamma_beta=2.0, sigma2_gamma_alpha=1.0, sigma2_gamma_beta=10.0,
                          remove_ambiguity_sites=False,
                          auto_finetune=True, times=0.1, rates=0.1, mixing=0.1, paras=0.1, RateParas=0.1, FossilErr=0.1,
                          num_of_burning=2000, sampling_frequency=2, number_of_samples=20000):

        if seq_type == "nucleotides":
            sequence_type = 0
        elif seq_type == "codons":
            sequence_type = 1
        elif seq_type == "aminoacids":
            sequence_type = 2
        else:
            raise(ValueError, "Wrong sequence type was set")
            
        if clock == "global":
            clock_type = 1
        elif clock == "independent":
            clock_type = 2
        elif clock == "correlated":
            clock_type = 3
        else:
            raise(ValueError, "Wrong clock type was set")    
            
        if model == "JC69":
            model_type = 0
        elif model == "K80":
            model_type = 1
        elif model == "F81":
            model_type = 2
        elif model == "F84":
            model_type = 3
        elif model == "HKY85":
            model_type = 4
        else:
            raise(ValueError, "Wrong model was set")       
            
        options = "seed = %i\n" % seed
        options += "seqfile = %s\n" % seq_file
        options += "treefile = %s\n" % tree_file
        options += "outfile = %s\n" % out_file

        options += "\n"

        options += "ndata = %i\n" % num_of_partitions
        options += "seqtype = %i * 0: nucleotides; 1:codons; 2:AAs\n" % sequence_type
        options += "usedata = %i * 0: no data; 1:seq like; 2:normal approximation; 3:out.BV (in.BV)\n" % use_data
        options += "clock = %i * 1: global clock; 2: independent rates; 3: correlated rates\n" % clock_type
        options += "RootAge = '%s' * safe constraint on root age, used if no fossil for root.\n" % root_age if root_age else ""

        options += "\n"

        options += "model = %i * 0:JC69, 1:K80, 2:F81, 3:F84, 4:HKY85\n" % model_type
        options += "alpha = %f * alpha for gamma rates at sites\n" % alpha_for_gamma_rates_at_sites
        options += "ncatG = %i * No. categories in discrete gamma\n" % ncatG

        options += "\n"

        options += "cleandata = %i * remove sites with ambiguity data (1:yes, 0:no)?\n" % (1 if remove_ambiguity_sites else 0)

        options += "\n"

        options += "BDparas = %f %f %f * birth, death, sampling\n" % (birth, death, sampling)
        options += "kappa_gamma = %f %f * gamma prior for kappa\n" % (kappa_gamma_alpha, kappa_gamma_beta)
        options += "alpha_gamma = %f %f * gamma prior for alpha\n" % (alpha_gamma_alpha, alpha_gamma_beta)

        options += "\n"

        """
        Choice of time unit. The time unit should be chosen such that the node ages are about 0.01-10.
        If the divergence times are around 100-1000MY, then 100MY may be one time unit. The priors
        on times and on rates and the fossil calibrations should all be specified based on your choice of
        the time scale. For example, if one time unit is 10MY, the following
        rgene_gamma = 2 20
        sigma2_gamma = 10 100
        * gamma prior for overall rates for genes
        * gamma prior for sigma^2 (for clock=2 or 3)
        means an overall average rate of 2/20 = 0.1 substitutions per site per 10MY or 10–8 substitutions
        per site per year, which is reasonable for mammalian mitochondrial genes. The gamma prior
        here has the shape parameter α = 2, and is fairly diffuse. If you change the time unit, you
        should keep the shape parameter fixed and change the scale parameter β to have the correct
        mean. In other words, to use one time unit to represent 100MY, the above should become
        rgene_gamma = 2 2
        sigma2_gamma = 10 100
        * gamma prior for overall rates for genes
        * gamma prior for sigma^2 (for clock=2 or 3)
        Note that under the independent-rates model (clock=2), the change of the time unit should not
        lead to a change to the prior for σ2, because σ2 is the variance of the log rate: the variance of the
        logarithm of the rate does not change when you rescale the rate by a constant. However, for the
        correlated-rates model (clock=3), the change of the time unit should also lead to a change to σ2:
        under that model, the variance of the log-normal distribution is tσ2, where t is the time gap
        separating the midpoints of the branches.
        When you change the time unit, the fossil calibrations in the tree file should be changed
        accordingly. While ideally one would want the biological results to be unchanged when one
        changes the time unit, we know that two components of the model are not invariant to the time
        scale: the log normal distribution for rates and the birth-death model for times. Nevertheless,
        tests by Mathieu Groussin did suggest that the choice of time scale has very minimal effects on
        the posterior time and rate estimates.

        """
        options += "rgene_gamma = %f %f * gammaDir prior for rate for genes\n" % (rgene_gamma_alpha, rgene_gamma_beta)
        if clock_type > 1:
            options += "sigma2_gamma = %f %f * gammaDir prior for sigma^2     (for clock=2 or 3)\n" % \
                       (sigma2_gamma_alpha, sigma2_gamma_beta)

        options += "\n"

        options += "finetune = %i: %f %f %f %f %f %f  * auto (0 or 1) : times, rates, mixing, paras, RateParas, FossilErr\n" % \
                   (1 if auto_finetune else 0, times, rates, mixing, paras, RateParas, FossilErr)

        options += "\n"

        options += "print = 1 * write mcmc and summary to disk (mcmc.out)\n"
        """
        burnin, sampfreq and nsample: in our example, the program will discard thefirst 2,000 iterations as burn-in,
        and then it will sample every 2 iterations until it has gathered 20,000 samples. In total, the MCMC will run
        for 2,000 + 2 x 20, 000 = 42, 000 iterations. Normally, you should gather between 10,000 to 20,000 samples
        for a good statistical summary. Large sample sizes (say 100,000)tend to waste a lot of hard drive space
        providing very little statistical improvement. It may also take a long time for the program to summarize
        the results. If you need to increase the length of the MCMC (to improve convergence), increase sampfreq
        but keep nsample at a reasonable value.
        """
        options += "burnin = %i\n" % num_of_burning
        options += "sampfreq = %i\n" % sampling_frequency
        options += "nsample = %i\n" % number_of_samples

        with open(ctl_file, "w") as ctl_fd:
            ctl_fd.write(options)

    def run_mcmctree(self, ctl_file):

        options = " %s" % ctl_file

        self.execute(options=options)

    def run(self, seq_file, tree_file, out_file, ctl_file, seed=-1, num_of_partitions=1,
            seq_type="nucleotides", use_data=1, clock="global", root_age=None,
            model="HKY85", ncatG=5, alpha_for_gamma_rates_at_sites=0.5,
            birth=1.0, death=1.0, sampling=0.1,
            alpha_gamma_alpha=1.0, alpha_gamma_beta=1.0, kappa_gamma_alpha=6.0, kappa_gamma_beta=2.0,
            rgene_gamma_alpha=2.0, rgene_gamma_beta=2.0, sigma2_gamma_alpha=1.0, sigma2_gamma_beta=10.0,
            remove_ambiguity_sites=False,
            auto_finetune=True, times=0.1, rates=0.1, mixing=0.1, paras=0.1, RateParas=0.1, FossilErr=0.1,
            num_of_burning=2000, sampling_frequency=2, number_of_samples=20000):

        self.generate_ctl_file(seq_file, tree_file, out_file, ctl_file, seed=seed, num_of_partitions=num_of_partitions,
                               seq_type=seq_type, use_data=use_data, clock=clock, root_age=root_age,
                               model=model, ncatG=ncatG, alpha_for_gamma_rates_at_sites=alpha_for_gamma_rates_at_sites,
                               birth=birth, death=death, sampling=sampling,
                               alpha_gamma_alpha=alpha_gamma_alpha, alpha_gamma_beta=alpha_gamma_beta,
                               kappa_gamma_alpha=kappa_gamma_alpha, kappa_gamma_beta=kappa_gamma_beta,
                               rgene_gamma_alpha=rgene_gamma_alpha, rgene_gamma_beta=rgene_gamma_beta,
                               sigma2_gamma_alpha=sigma2_gamma_alpha, sigma2_gamma_beta=sigma2_gamma_beta,
                               remove_ambiguity_sites=remove_ambiguity_sites,
                               auto_finetune=auto_finetune, times=times, rates=rates, mixing=mixing, paras=paras,
                               RateParas=RateParas, FossilErr=FossilErr,
                               num_of_burning=num_of_burning, sampling_frequency=sampling_frequency,
                               number_of_samples=number_of_samples)

        options = " %s" % ctl_file

        self.execute(options=options)