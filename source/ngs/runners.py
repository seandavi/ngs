class JointSNVMix(object):
    """
    Run JointSNVMix on a pair of tumor/normal bam files
    """
    def __init__(self,config):
        self.reference_genome=config['reference']
        self.executable = config['jointsnvmix']['executable']
        self.priors = config['jointsnvmix']['priors']
        self.initial_params = config['jointsnvmix']['initial_params']
        
    def train(self,
              normal_bam,
              tumor_bam,
              output_param_name,
              other_args=None):
        """Train the JoinSNVMix caller"""
        cmd = "%s train joint_snv_mix_two " % (self.executable)
        if(other_args is not None):
            cmd = cmd + other_args + " "
        cmd = cmd + """%s %s %s %s %s %s""" % (self.reference_genome,
                                               normal_bam,
                                               tumor_bam,
                                               self.priors,
                                               self.initial_params,
                                               output_param_name)
        return(cmd)
    
    def classify(self,
                 normal_bam,
                 tumor_bam,
                 param_file_name,
                 output_file_name,
                 other_args=None):
        """Run the JoinSNVMix caller

        :param normal_bam: The normal bam file name
        :param tumor_bam: The tumor bam file name
        :param output_file_name: The output file name
        :param other_args: String containing any other arguments to JointSNVMix.  This is simply passed on to the command line as a string.

        """
        cmd = "%s classify joint_snv_mix_two " % (self.executable)
        if(other_args is not None):
            cmd = cmd + other_args + " "
        cmd = cmd + """%s %s %s %s %s""" % (self.reference_genome,
                                            normal_bam,
                                            tumor_bam,
                                            param_file_name,
                                            output_file_name)
        return(cmd)
