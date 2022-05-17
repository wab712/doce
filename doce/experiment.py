import types
import inspect
import os
import time
import datetime
import doce
import ast
import glob


class Experiment():
  """Stores high level information about the experiment and tools to control the processing and storage of data.

  The experiment class displays high level information about the experiment such as its name, description, author, author's email address, and run identification. Information about storage of data is specified using the experiment.path name_space. It also stores one or several Plan objects and a Metric object to respectively specify the experimental plans and the metrics considered in the experiment.

  See Also
  --------

  doce.Plan, doce.metric.Metric

  Examples
  --------

  >>> import doce
  >>> e=doce.Experiment()
  >>> e.name='my_experiment'
  >>> e.author='Mathieu Lagrange'
  >>> e.address='mathieu.lagrange@ls2n.fr'
  >>> e.path.processing='/tmp'
  >>> print(e)
      name: my_experiment
    description
    author: Mathieu Lagrange
    address: mathieu.lagrange@ls2n.fr
    version: 0.1
    status:
      run_id: ...
      verbose: 0
    parameter
    metric
    path:
      code_raw: ...
      code: ...
      archive_raw:
      archive:
      export_raw: export
      export: export
      processing_raw: /tmp
      processing: /tmp
    host: []


  Each level can be complemented with new members to store specific information:

  >>> e.specific_info = 'stuff'
  >>> import types
  >>> e.my_data = types.SimpleNamespace()
  >>> e.my_data.info1= 1
  >>> e.my_data.info2= 2
  >>> print(e)
    name: my_experiment
    description
    author: Mathieu Lagrange
    address: mathieu.lagrange@ls2n.fr
    version: 0.1
    status:
      run_id: ...
      verbose: 0
    parameter
    metric
    path:
      code_raw: ...
      code: ...
      archive_raw:
      archive:
      export_raw: export
      export: export
      processing_raw: /tmp
      processing: /tmp
    host: []
    specific_info: stuff
    my_data:
      info1: 1
      info2: 2
  """

  def __init__(
    self, **description
    ):
    # list of attributes (preserving order of insertion for antique versions of python)
    self._atrs = []
    self._plan = doce.Plan()
    self._plans = []
    self.name = ''
    self.description = ''
    self.author = 'no name'
    self.address = 'noname@noorg.org'
    self.version = '0.1'

    self.status = types.SimpleNamespace()
    self.status.run_id = str(int((time.time()-datetime.datetime(2020,1,1,0,0).timestamp())/60))
    self.status.verbose = 0

    self.parameter = types.SimpleNamespace()
    self.metric = doce.Metric()
    self.path = Path()
    self.path.code = os.getcwd()
    self.path.archive = ''
    self.path.export = 'export'
    self.host = []
    self._archive_path = ''
    self._gmail_id = 'expcode.mailer'
    self._gmail_app_password = 'tagsqtlirkznoxro'
    self._default_server_run_argument =  {}
    self._resume = False

    self._display = types.SimpleNamespace()
    self._display.factor_format_in_reduce = 'long'
    self._display.metric_format_in_reduce = 'long'
    self._display.metric_precision = 2
    self._display.factor_format_in_reduceLength = 2
    self._display.metric_format_in_reduceLength = 2
    self._display.show_row_index = True
    self._display.highlight = True
    self._display.bar = False
    self._display.pValue = 0.05

    for field, value in description.items():
      self.__setattr__(field, value)




  def __setattr__(
    self,
    name,
    value
    ):
    if not hasattr(self, name) and name[0] != '_':
      self._atrs.append(name)
    return object.__setattr__(self, name, value)

  # def expand_path(
  #   self
  #   ):
  #   """
  #
  #   Examples
  #   --------
  #
  #   >>> import doce
  #   >>> import os
  #   >>> e=doce.Experiment()
  #   >>> e.name = 'experiment'
  #   >>> e.path.processing = '/tmp/'+e.name+'/processing'
  #   >>> e.path.output = '/tmp/'+e.name+'/output'
  #   >>> e.set_path(force=_true)
  #   >>> os.listdir('/tmp/'+e.name)
  #   ['processing', 'output']
  #   """
  #   for sns in self.__getattribute__('path').__dict__.keys():
  #     self.__getattribute__('path') = os.path.abspath(os.path.expanduser(self.__getattribute__('path').__getattribute__(sns)))

  def set_path(
    self,
    name,
    path,
    force=False
    ):
    """Create directories whose path described in experiment.path are not reachable.

    For each path set in experiment.path, create the directory if not reachable. The user may be prompted before creation.

  	Parameters
  	----------

    force : bool
      If True, do not prompt the user before creating the missing directories.

      If False, prompt the user before creation of each missing directory (default).

    Examples
    --------

    >>> import doce
    >>> import os
    >>> e=doce.Experiment()
    >>> e.name = 'experiment'
    >>> e.set_path('processing', '/tmp/'+e.name+'/processing', force=True)
    >>> e.set_path('output', '/tmp/'+e.name+'/output', force=True)
    >>> os.listdir('/tmp/'+e.name)
    ['processing', 'output']
    """
    # for sns in self.__getattribute__('path').__dict__.keys():
    self.path.__setattr__(name, path)

    path = os.path.abspath(os.path.expanduser(path))
    if path:
      if path.endswith('.h5'):
        path = os.path.dirname(os.path.abspath(path))
      else:
        if not path.endswith('/'):
          if not path.endswith('\\'):
            if '\\' in path:
              path = path+'\\'
              self.path.__setattr__(name, path)
            else:
              path = path+'/'
              self.path.__setattr__(name, path)

      if not os.path.exists(path):
        if force or doce.util.query_yes_no('The '+name+' path: '+path+' does not exist. Do you want to create it ?'):
          os.makedirs(path)
          if not force:
            print('Path succesfully created.')

  def __str__(
    self,
    format='str'
    ):
    """Provide a textual description of the experiment

    List all members of the class and theirs values

    parameters
    ----------
    format : str
      If 'str', return the description as a string.

      If 'html', return the description with an html format.

  	Returns
  	-------
    description : str
        If format == 'str' : a carriage return separated enumaration of the members of the class experiment.

        If format == 'html' : an html version of the description

  	Examples
  	--------

    >>> import doce
    >>> print(doce.Experiment())
    name
    description
    author: no name
    address: noname@noorg.org
    version: 0.1
    status:
      run_id: ...
      verbose: 0
    parameter
    metric
    path:
      code_raw: ...
      code: ...
      archive_raw:
      archive:
      export_raw: export
      export: export
    host: []

    >>> import doce
    >>> doce.Experiment().__str__(format='html')
        '<div>name</div><div>description</div><div>author: no name</div><div>address: noname@noorg.org</div><div>version: 0.1</div><div>status:</div><div>  run_id: ...</div><div>  verbose: 0</div><div>parameter</div><div>metric</div><div>path:</div><div>  code_raw: ...</div><div>  code: ...</div><div>  archive_raw: </div><div>  archive: </div><div>  export_raw: export</div><div>  export: export</div><div>host: []</div><div></div>'
    """
    description = ''
    for atr in self._atrs:
      if type(inspect.getattr_static(self, atr)) != types.FunctionType:
        if type(self.__getattribute__(atr)) in [types.SimpleNamespace, Path]:
          description += atr
          if len(self.__getattribute__(atr).__dict__.keys()):
            description+=':'
          description+='\r\n'
          for sns in self.__getattribute__(atr).__dict__.keys():
            description+='  '+sns+': '+str(self.__getattribute__(atr).__getattribute__(sns))+'\r\n'
        elif isinstance(self.__getattribute__(atr), str) or isinstance(self.__getattribute__(atr), list):
          description+=atr
          if len(str(self.__getattribute__(atr))):
            description +=': '+str(self.__getattribute__(atr))
          description += '\r\n'
        else:
          description+=atr
          if len(str(self.__getattribute__(atr))):
            description +=': \r\n'+str(self.__getattribute__(atr))
          description += '\r\n'
    if format == 'html':
      description = '<div>'+description.replace('\r\n', '</div><div>').replace('\t', '&emsp;')+'</div>'
    return description

  def send_mail(
    self,
    title='',
    body=''):
    """Send an email to the email address given in experiment.address.

    Send an email to the experiment.address email address using the smtp service from gmail. For privacy, please consider using a dedicated gmail account by setting experiment._gmail_id and experiment._gmail_app_password. For this, you will need to create a gmail account, set two-step validation and allow connection with app password (see https://support.google.com/accounts/answer/185833?hl=en).

    Parameters
    ----------

    title : str
      the title of the email in plain text format

    body : str
      the body of the email in html format

    Examples
    --------
    >>> import doce
    >>> e=doce.Experiment()
    >>> e.address = 'mathieu.lagrange@cnrs.fr'
    >>> e.send_mail('hello', '<div> good day </div>')
    Sent message entitled: [doce]  id ... hello ...

    """

    import smtplib

    header = 'From: doce mailer <'+self._gmail_id+'@gmail.com> \r\nTo: '+self.author+' '+self.address+'\r\nMIME-Version: 1.0 \r\nContent-type: text/html \r\nSubject: [doce] '+self.name+' id '+self.status.run_id+' '+title+'\r\n'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(self._gmail_id+'@gmail.com', self._gmail_app_password)
    server.sendmail(self._gmail_id, self.address, header+body+'<h3> '+self.__str__(format = 'html')+'</h3>')
    server.quit
    print('Sent message entitled: [doce] '+self.name+' id '+self.status.run_id+' '+title+' on '+time.ctime(time.time()))

  def do(
    self,
    selector,
    function=None,
    *parameters,
    nb_jobs=1,
    progress='d',
    log_file_name='',
    mail_interval=0
    ):
    """Operate the function with parameters on the :term:`settings<setting>` set generated using :term:`selector`.

    Operate a given function on the setting set generated using selector. The setting set can be browsed in parallel by setting nb_jobs>1. If log_file_name is not empty, a faulty setting do not stop the execution, the error is stored and another setting is executed. If progress is set to True, a graphical display of the progress through the setting set is displayed.

    This function is essentially a wrapper to the function :meth:`doce.Plan.do`.

    Parameters
    ----------

    selector : a list of literals or a list of lists of literals
      :term:`selector` used to specify the :term:`settings<setting>` set

    function : function(:class:`~doce.Plan`, :class:`~doce.Experiment`, \*parameters) (optional)
      A function that operates on a given setting within the experiment environnment with optional parameters.

      If None, a description of the given setting is shown.

    *parameters : any type (optional)
      parameters to be given to the function.

    nb_jobs : int > 0 (optional)
      number of jobs.

      If nb_jobs = 1, the setting set is browsed sequentially in a depth first traversal of the settings tree (default).

      If nb_jobs > 1, the settings set is browsed randomly, and settings are distributed over the different processes.

    progress : str (optional)
      display progress of scheduling the setting set.

      If str has an m, show the selector of the current setting.
      If str has an d, show a textual description of the current setting (default).

    log_file_name : str (optional)
      path to a file where potential errors will be logged.

      If empty, the execution is stopped on the first faulty setting (default).

      If not empty, the execution is not stopped on a faulty setting, and the error is logged in the log_file_name file.

    mail_interval : float (optional)
      interval for sending email about the status of the run.

      If 0, no email is sent (default).

      It >0, an email is sent as soon as an setting is done and the difference between the current time and the time the last mail was sent is larger than mail_interval.

    See Also
    --------

    doce.Plan.do

    Examples
    --------

    >>> import time
    >>> import random
    >>> import doce

    >>> e=doce.Experiment()
    >>> e.add_plan('plan', factor1=[1, 3], factor2=[2, 5])

    >>> # this function displays the sum of the two modalities of the current setting
    >>> def my_function(setting, experiment):
    ...  print('{}+{}={}'.format(setting.factor1, setting.factor2, setting.factor1+setting.factor2))

    >>> # sequential execution of settings
    >>> nb_failed = e.do([], my_function, nb_jobs=1, progress='')
    1+2=3
    1+5=6
    3+2=5
    3+5=8
    >>> # arbitrary order execution of settings due to the parallelization
    >>> nb_failed = e.do([], my_function, nb_jobs=3, progress='') # doctest: +SKIP
    3+2=5
    1+5=6
    1+2=3
    3+5=8
    """

    return self._plan.select(selector).do(function, self, *parameters, nb_jobs=nb_jobs, progress=progress, log_file_name=log_file_name, mail_interval=mail_interval)

  def select(self, selector, show=False):
    experiment_id = 'all'
    if '/' in selector:
      s = selector.split('/')
      experiment_id = s[0]
      if len(s)>1:
        selector = s[1]
        try:
          selector = ast.literal_eval(selector)
        except:
          pass
      else:
        selector = ''
    self.selector = selector

    plans = self.plans()
    if len(plans)==1:
      self._plan = getattr(self, plans[0])
    else:
      if experiment_id == 'all':
        oPlans = []
        for p in plans:
          if show:
            print('Plan '+p+':')
            print(getattr(self, p).as_panda_frame())
          oPlans.append(getattr(self, p))
        self._plan = self._plan.merge(oPlans)
        if show and len(plans)>1:
          print('Those plans can be selected using the selector parameter.')
          print('Otherwise the merged plan is considered: ')
      else:
        if experiment_id.isnumeric():
          experiment_id = plans[int(experiment_id)]
        print('Plan '+experiment_id+' is selected')
        self._plan = getattr(self, experiment_id)
    self._plan.check()
    if show:
      print(self._plan.as_panda_frame())
    return self._plan.select(selector)

  def clean_data_sink(
    self,
    path,
    selector=[],
    reverse=False,
    force=False,
    keep=False,
    wildcard='*',
    setting_encoding={},
    archive_path = None,
    verbose=0
    ):
    """ Perform a cleaning of a data sink (directory or h5 file).

    This method is essentially a wrapper to :meth:`doce._plan.clean_data_sink`.

    Parameters
    ----------

    path : str
      If has a / or \\\, a valid path to a directory or .h5 file.

      If has no / or \\\, a member of the name_space self.path.

    selector : a list of literals or a list of lists of literals (optional)
      :term:`selector` used to specify the :term:`settings<setting>` set

    reverse : bool (optional)
      If False, remove any entry corresponding to the setting set (default).

      If True, remove all entries except the ones corresponding to the setting set.

    force: bool (optional)
      If False, prompt the user before modifying the data sink (default).

      If True, do not prompt the user before modifying the data sink.

    wildcard : str (optional)
      end of the wildcard used to select the entries to remove or to keep (default: '*').

    setting_encoding : dict (optional)
      format of the id describing the :term:`setting`. Please refer to :meth:`doce.Plan.id` for further information.

    archive_path : str (optional)
      If not None, specify an existing directory where the specified data will be moved.

      If None, the path doce.Experiment._archive_path is used (default).

    See Also
    --------

    doce._plan.clean_data_sink, doce.Plan.id

    Examples
    --------

    >>> import doce
    >>> import numpy as np
    >>> import os
    >>> e=doce.Experiment()
    >>> e.set_path('output', '/tmp/test', force=True)
    >>> e.add_plan('plan', factor1=[1, 3], factor2=[2, 4])
    >>> def my_function(setting, experiment):
    ...   np.save(experiment.path.output+'/'+setting.identifier()+'_sum.npy', setting.factor1+setting.factor2)
    ...   np.save(experiment.path.output+'/'+setting.identifier()+'_mult.npy', setting.factor1*setting.factor2)
    >>> nb_failed = e.do([], my_function, progress='')
    >>> os.listdir(e.path.output)
    ['factor1=1+factor2=4_mult.npy', 'factor1=1+factor2=4_sum.npy', 'factor1=3+factor2=4_sum.npy', 'factor1=1+factor2=2_mult.npy', 'factor1=1+factor2=2_sum.npy', 'factor1=3+factor2=2_mult.npy', 'factor1=3+factor2=4_mult.npy', 'factor1=3+factor2=2_sum.npy']

    >>> e.clean_data_sink('output', [0], force=True)
    >>> os.listdir(e.path.output)
    ['factor1=3+factor2=4_sum.npy', 'factor1=3+factor2=2_mult.npy', 'factor1=3+factor2=4_mult.npy', 'factor1=3+factor2=2_sum.npy']

    >>> e.clean_data_sink('output', [1, 1], force=True, reverse=True, wildcard='*mult*')
    >>> os.listdir(e.path.output)
    ['factor1=3+factor2=4_sum.npy', 'factor1=3+factor2=4_mult.npy', 'factor1=3+factor2=2_sum.npy']

    Here, we remove all the files that match the wildcard *mult* in the directory /tmp/test that do not correspond to the settings that have the first factor set to the second modality and the second factor set to the second modality.

    >>> import doce
    >>> import tables as tb
    >>> e=doce.Experiment()
    >>> e.set_path('output', '/tmp/test.h5')
    >>> e.add_plan('plan', factor1=[1, 3], factor2=[2, 4])
    >>> e.set_metrics(sum = [''], mult = [''])
    >>> def my_function(setting, experiment):
    ...   h5 = tb.open_file(experiment.path.output, mode='a')
    ...   sg = experiment.metric.add_setting_group(h5, setting, metric_dimension={'sum': 1, 'mult': 1})
    ...   sg.sum[0] = setting.factor1+setting.factor2
    ...   sg.mult[0] = setting.factor1*setting.factor2
    ...   h5.close()
    >>> nb_failed = e.do([], my_function, progress='')
    >>> h5 = tb.open_file(e.path.output, mode='r')
    >>> print(h5)
    /tmp/test.h5 (File) ''
    Last modif.: '...'
    Object Tree:
    / (RootGroup) ''
    /factor1_1_factor2_2 (Group) 'factor1=1+factor2=2'
    /factor1_1_factor2_2/mult (Array(1,)) 'mult'
    /factor1_1_factor2_2/sum (Array(1,)) 'sum'
    /factor1_1_factor2_4 (Group) 'factor1=1+factor2=4'
    /factor1_1_factor2_4/mult (Array(1,)) 'mult'
    /factor1_1_factor2_4/sum (Array(1,)) 'sum'
    /factor1_3_factor2_2 (Group) 'factor1=3+factor2=2'
    /factor1_3_factor2_2/mult (Array(1,)) 'mult'
    /factor1_3_factor2_2/sum (Array(1,)) 'sum'
    /factor1_3_factor2_4 (Group) 'factor1=3+factor2=4'
    /factor1_3_factor2_4/mult (Array(1,)) 'mult'
    /factor1_3_factor2_4/sum (Array(1,)) 'sum'
    >>> h5.close()

    >>> e.clean_data_sink('output', [0], force=True)
    >>> h5 = tb.open_file(e.path.output, mode='r')
    >>> print(h5)
    /tmp/test.h5 (File) ''
    Last modif.: '...'
    Object Tree:
    / (RootGroup) ''
    /factor1_3_factor2_2 (Group) 'factor1=3+factor2=2'
    /factor1_3_factor2_2/mult (Array(1,)) 'mult'
    /factor1_3_factor2_2/sum (Array(1,)) 'sum'
    /factor1_3_factor2_4 (Group) 'factor1=3+factor2=4'
    /factor1_3_factor2_4/mult (Array(1,)) 'mult'
    /factor1_3_factor2_4/sum (Array(1,)) 'sum'
    >>> h5.close()

    >>> e.clean_data_sink('output', [1, 1], force=True, reverse=True, wildcard='*mult*')
    >>> h5 = tb.open_file(e.path.output, mode='r')
    >>> print(h5)
    /tmp/test.h5 (File) ''
    Last modif.: '...'
    Object Tree:
    / (RootGroup) ''
    /factor1_3_factor2_4 (Group) 'factor1=3+factor2=4'
    /factor1_3_factor2_4/mult (Array(1,)) 'mult'
    /factor1_3_factor2_4/sum (Array(1,)) 'sum'
    >>> h5.close()

    Here, the same operations are conducted on a h5 file.
    """

    if '/' not in path and '\\' not in path:
      path = self.__getattribute__('path').__getattribute__(path)
    if path:
      self._plan.select(selector).clean_data_sink(path, reverse=reverse, force=force, keep=keep, wildcard=wildcard, setting_encoding=setting_encoding, archive_path=archive_path, verbose=verbose)

  def plans(self):
    # names = []
    # for attribute in dir(self):
    #   if attribute[0] != '_' and isinstance(getattr(self, attribute), doce.Plan):
    #     names.append(attribute)
    return self._plans

  def add_plan(self, name, **kwargs):
    self.__setattr__(name, doce.Plan(**kwargs))
    self._plan = getattr(self, name)
    self._plans.append(name)

  def set_metrics(self, **kwargs):
    self.__setattr__('metric', doce.Metric(**kwargs))

  def default(self, plan='', factor='', modality=''):
    getattr(self, plan).default(factor, modality)

  def skip_setting(self, setting):
    if self._resume:
      for path in self.__getattribute__('path').__dict__.keys():
          if path.endswith('.h5'):
            print('todo')
          else:
            if path not in ['export', 'export_raw', 'archive', 'archive_raw', 'code', 'code_raw']:
              check = glob.glob(self.path.__getattribute__(path)+setting.identifier()+'_*.npy')
              if check:
                return True
    return False

  def get(self, metric='', selector=[], path=''):
    """ Get the metric vector from an .npy or a group of a .h5 file.

    Get the metric vector as a numpy array from an .npy or a group of a .h5 file.

    Parameters
    ----------

    metric: str
      The name of the metric. Must be a member of the doce.metric.Metric object.

    selector: list
      Settings selector.

    path: str
      Name of path as defined in the experiement or a valid path to a directory in the case of .npy storage, or a valid path to an .h5 file in the case of hdf5 storage.

    Returns
    -------

    setting_metric: list of np.Array
      stores for each valid setting an np.Array with the values of the metric selected.

    setting_description: list of list of str
      stores for each valid setting, a compact description of the modalities of each factors. The factors with the same modality accross all the set of settings is stored in constant_setting_description.

    constant_setting_description: str
      compact description of the factors with the same modality accross all the set of settings.

    Examples
    --------

    >>> import doce
    >>> import numpy as np
    >>> import pandas as pd

    >>> experiment = doce.experiment.Experiment()
    >>> experiment.name = 'example'
    >>> experiment.set_path('output', '/tmp/'+experiment.name+'/', force=True)
    >>> experiment.add_plan('plan', f1 = [1, 2], f2 = [1, 2, 3])
    >>> experiment.set_metrics(m1 = ['mean', 'std'], m2 = ['min', 'argmin'])

    >>> def process(setting, experiment):
    ...  metric1 = setting.f1+setting.f2+np.random.randn(100)
    ...  metric2 = setting.f1*setting.f2*np.random.randn(100)
    ...  np.save(experiment.path.output+setting.identifier()+'_m1.npy', metric1)
    ...  np.save(experiment.path.output+setting.identifier()+'_m2.npy', metric2)
    >>> nb_failed = experiment.do([], process, progress='')

    >>> (setting_metric, setting_description, constant_setting_description) = experiment.get(metric = 'm1', selector = [1], path='output')
    >>> print(constant_setting_description)
    f1=2
    >>> print(setting_description)
    ['f2=1', 'f2=2', 'f2=3']
    >>> print(len(setting_metric))
    3
    >>> print(setting_metric[0].shape)
    (100,)
    """

    if path:
        if not ('\/' in path or '\\' in path):
          path = getattr(self.path, path)
        return self.metric.get(
          metric,
          settings=self.plan.select(selector),
          path=path
          )
    else:
      data = []
      settings = []
      for path in self.path.__dict__.keys():
        if not path.endswith('_raw'):
          path = getattr(self.path, path)
          (dp, sp, hp) = self.metric.get(
            metric,
            settings=self.plan.select(selector),
            path=path
            )
          if dp:
            for d in dp:
              data.append(d)
            for s in sp:
              settings.append(s)

      return (data, settings, hp)



  # def clean(
  #   self,
  #   selector=[],
  #   reverse=False,
  #   force=False,
  #   wildcard='*',
  #   setting_encoding={},
  #   archive_path = None
  #   ):
  #   """Clean all relevant directories specified in the name_space doce.Experiment.experiment.path.
  #
  #   Apply :meth:`doce._experiment.clean_data_sink` on each relevant directories specified in the name_space doce.Experiment.path.
  #
  #   See Also
  #   --------
  #
  #   doce._experiment.clean_data_sink
  #
  #   Examples
  #   --------
  #
  #   >>> import doce
  #   >>> e=doce.Experiment()
  #   >>> e.path.output = '/tmp/test'
  #   >>> e.set_path()
  #   >>> e.clean()
  #   checking input path
  #   checking processing path
  #   checking storage path
  #   checking output path
  #
  #   """
  #   for sns in self.__getattribute__('path').__dict__.keys():
  #     print('checking '+sns+' path')
  #     self.clean_data_sink(sns, selector, reverse, force, wildcard, setting_encoding,
  #     archive_path)

class Path:
    def __setattr__(
      self,
      name,
      value
      ):
      object.__setattr__(self, name+'_raw', value)
      object.__setattr__(self, name, os.path.expanduser(value))


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    # doctest.run_docstring_examples(doce.Experiment, globals(), optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)
