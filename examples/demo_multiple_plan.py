import doce
import time
import numpy as np
from pathlib import Path

# invoke the command line management of the doce package
if __name__ == "__main__":
  doce.cli.main()

# define the doce environnment
def set(args=None):
  # define the experiment
  experiment = doce.Experiment(
    name = 'demo_multiple_plan',
    purpose = 'using multple plans using the doce package',
    author = 'mathieu Lagrange',
    address = 'mathieu.lagrange@ls2n.fr',
  )
  # set acces paths (here only storage is needed)
  experiment.setPath('output', '/tmp/'+experiment.name+'/', force=True)
  # set the "svm" plan
  experiment.addPlan('svm',
    classifier = ['svm'],
    c = [1., 0.1, 0.01]
  )
  # set the "deep" plan
  experiment.addPlan('deep',
    classifier = ['cnn', 'lstm'],
    n_layers = [2, 4, 8],
    dropout = [0, 1]
  )
  # set the metrics
  experiment.setMetrics(
    accuracy = ['mean%']
  )
  return experiment

def step(setting, experiment):
  # the accuracy  is a function of cnn_type, and use of dropout
  if setting.classifier == 'svm':
    accuracy = setting.c*np.random.random_sample(10)/6
  else:
    accuracy = (len(setting.classifier)+setting.dropout+np.random.random_sample(10))/6

  np.save(experiment.path.output+setting.id()+'_accuracy.npy', accuracy)