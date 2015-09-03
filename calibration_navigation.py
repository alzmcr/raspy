import pandas as pd
import numpy as np
from model import Model
from accelerometer import process
from time import sleep

def train_data():
    from navigation import r
    r.m1.use_pwm = False; r.m2.use_pwm = False
    r.init_log()
    sleep(1)
    r.left(2); sleep(1)
    r.right(2); sleep(1)
    r.fw(2); sleep(1)
    r.rw(2); sleep(1)
    r.left(2); sleep(1)
    r.right(2); sleep(1)
    r.fw(2); sleep(1)
    r.rw(2); sleep(1)
    r.left(2); sleep(1)
    r.right(2); sleep(1)
    r.fw(2); sleep(1)
    r.rw(2); sleep(1)
    r.save_log(savepath='data/navigation_calibration/')

def readfromfiles(files):
    def readandname(f):
        data = pd.DataFrame.from_csv(f)
        data['fname'] = f.split('/')[-1]
        return data

    data = pd.concat([readandname(f) for f in files]); data.index.name = 'time'
    return data

def calibrate(r, model=None):
    # load default model
    if model is None: model = Model.load('models/rover_calibration.pkl')
    # calibration movements | left & right using only one motor (easier)
    r.init_log(); sleep(1)
    r.left(2,motor=1); sleep(1); r.left(2,motor=2); sleep(1)    # sequence: 1,3
    r.right(2,motor=1); sleep(1); r.right(2,motor=2); sleep(1)  # sequence: 5,7
    # end of calibration movements
    # get log, process data and remove stops
    logdata = r.save_log(); logdata['fname'] = 'dropme'
    logdata.index.name = 'time'; data = process_df(logdata)
    preds = data[model.features].groupby(level=['seq']).apply(lambda x: model.labels[model.predict_proba(x).sum(axis=0).argmax()])

    # check if movements are correctly calibrated
    if preds[1] == 'left' and preds[3] == 'left' and preds[5] == 'right' and preds[7] == 'right':
        print "Rover calibrated correctly (Motor1 gpio1_is_fw: %s | Motor2 gpio1_is_fw: %s)" % (r.m1.gpio1_is_fw, r.m2.gpio1_is_fw)
        return True
    else:
        if preds[1] == 'left' and preds[5] == 'right':
            r.m2.gpio1_is_fw = not r.m2.gpio1_is_fw
            print "Rover re-calibrated changing direction of Motor 1, testing..."
            return calibrate(r, model)
        elif preds[3] == 'left' and preds[7] == 'right':
            r.m1.gpio1_is_fw = not r.m1.gpio1_is_fw
            print "Rover re-calibrated changing direction of Motor 2, testing..."
            return calibrate(r, model)
        else:
            print "Error calibrating"
            return False

def process_df(df):
    # fill action and sequence for labels
    df[['action','seq']] = df[['action','seq']].ffill()
    df = df.reset_index().set_index(['fname','seq','action','time']).sort_index()
    # process features
    #df[['ax','ay','az','gx','gy','gz','mx','my','mz']] = df[['ax','ay','az','gx','gy','gz','mx','my','mz']].apply(process)
    # create new features
    df[['ax5','ay5','az5','gx5','gy5','gz5','mx5','my5','mz5']] = df.groupby(level=['fname','seq','action'])[['ax','ay','az','gx','gy','gz','mx','my','mz']].apply(lambda x: pd.rolling_mean(x,10,1,center=True))

    # cleaning
    df[df.columns] = df.groupby(level=['fname','seq','action'])[df.columns].ffill().bfill()
    idx = df[['ax','ay','az','gx','gy','gz','mx','my','mz']].isnull().sum(axis=1) == 0
    df = df[idx].query('action!="stop"')#.query('action in ("fw","rw")')
    # return df
    return df

if __name__ == '__main__':
    from sklearn import ensemble
    files = ['carlog_20150811_224249','carlog_20150811_224349','carlog_20150811_224452','carlog_20150811_224550',
             'carlog_20150811_224819','carlog_20150811_224909','carlog_20150811_234306','carlog_20150811_234353',
             'carlog_20150811_234550','carlog_20150812_213712',
    ]
    files = ['carlog_20150901_215418','carlog_20150901_223121']
    files = ['data/navigation_calibration/'+f+'.csv' for f in files]


    data = process_df(readfromfiles(files))

    rf = ensemble.RandomForestClassifier(random_state=3); rf.min_samples_leaf = 1; rf.n_estimators=10; df = data; model = rf
    X = data[['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'mx', 'my', 'mz', 'ax5', 'ay5', 'az5', 'gx5', 'gy5', 'gz5', 'mx5', 'my5', 'mz5']]
    y = data.reset_index()['action']

    m = Model.fit_create(rf, X, y)
    m.dump('models/rover_calibration.pkl')

    df = data; model = m


def train_model(df, model):
    X = df[['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'mx', 'my', 'mz', 'ax5', 'ay5', 'az5', 'gx5', 'gy5', 'gz5', 'mx5', 'my5', 'mz5']].diff(2).fillna(0)                  # train set
    y = df.reset_index()['action']                              # target
    files = df.reset_index()['fname'].unique().tolist()         # files used for train the model

    trscores, cvscores = [],[]
    for i in range(len(files)):
        icv = X.reset_index()['fname'].values == files[i]; itr = -icv
        model = model.fit(X[itr],y[itr])
        x1 = X[icv].groupby(level=['fname','seq','action']).apply(lambda x: model.labels[model.predict_proba(x).mean(axis=0).argmax()])
        x2 = X[itr].groupby(level=['fname','seq','action']).apply(lambda x: model.labels[model.predict_proba(x).mean(axis=0).argmax()])
        cvscores.append((x1.reset_index()[0]==x1.reset_index().action).mean())
        trscores.append((x2.reset_index()[0]==x2.reset_index().action).mean())
    print np.mean(trscores), np.mean(cvscores)

    return model.fit(X,y)


if False:
    import matplotlib.pyplot as plt
    for i,col in enumerate(['ax5','ay5','az5','gx5','gy5','gz5','mx5','my5','mz5']):
        plt.subplot(911 + i)
        data.reset_index().set_index('time')[col].plot()