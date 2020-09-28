import explanes as el
import numpy as np
import tables as tb
import pandas as pd

experiment = el.experiment.Experiment()
experiment.project.name = 'example'
experiment.path.output = '/tmp/'+experiment.project.name+'.h5'
experiment.factor.f1 = [1, 2]
experiment.factor.f2 = [1, 2, 3]
experiment.metric.m1 = ['mean', 'std']
experiment.metric.m2 = ['min', 'argmin']

def process(setting, experiment):
  h5 = tb.open_file(experiment.path.output, mode='a')
  sg = experiment.metric.h5addSetting(h5, setting,
      metricDimensions = [100, 100])
  sg.m1[:] = setting.f1+setting.f2+np.random.randn(100)
  sg.m2[:] = setting.f1*setting.f2*np.random.randn(100)
  h5.close()

experiment.makePaths()
experiment.do([], process, progress=False)

h5 = tb.open_file(experiment.path.output, mode='r')
print(h5)
h5.close()

(table, columns, header) = experiment.metric.reduce(experiment.factor.settings(), experiment.path.output)

df = pd.DataFrame(table, columns=columns).round(decimals=2)
print(df)