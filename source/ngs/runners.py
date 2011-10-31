class JointSNVMix(object):
    
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
        cmd = "%s classify joint_snv_mix_two " % (self.executable)
        if(other_args is not None):
            cmd = cmd + other_args + " "
        cmd = cmd + """%s %s %s %s %s""" % (self.reference_genome,
                                            normal_bam,
                                            tumor_bam,
                                            param_file_name,
                                            output_file_name)
        return(cmd)
