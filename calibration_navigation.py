import pandas as pd
from model import Model
from accelerometer import process
from time import sleep

def train_data():
    from navigation import r
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
    data = process_df(r.save_log(savefile=False))
    preds = data[model.features].groupby(level=['seq']).apply(lambda x: model.labels[model.predict_proba(x).sum(axis=0).argmax()])

    # check if movements are correctly calibrated
    if preds[1] == 'left' and preds[3] == 'left' and preds[5] == 'right' and preds[7] == 'right':
        print "Rover calibrated correctly (Motor1 gpio1_is_fw: %s | Motor2 gpio1_is_fw: %s)" % (r.m1.gpio1_is_fw, r.m2.gpio1_is_fw)
        return True
    else:
        if preds[1] == 'left' and preds[5] == 'right':
            r.m1.gpio1_is_fw = -r.m1.gpio1_is_fw
            print "Rover re-calibrated changing direction of Motor 1, testing..."
            return calibrate(r, model)
        elif preds[3] == 'left' and preds[7] == 'right':
            r.m2.gpio1_is_fw = -r.m2.gpio1_is_fw
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
    df[['x','y','z']] = df[['x','y','z']].apply(process)
    # create new features
    df[['x5','y5','z5']] = df.groupby(level=['fname','seq','action'])[['x','y','z']].apply(lambda x: pd.rolling_mean(x,5,1))
    # cleaning
    df[df.columns] = df.groupby(level=['fname','seq','action'])[df.columns].ffill().bfill()
    idx = df[['x','y','z']].isnull().sum(axis=1) == 0
    df = df[idx].query('action!="stop"').query('action in ("left","right")')
    # return df
    return df

if __name__ == '__main__':
    from sklearn import ensemble
    files = ['carlog_20150809_172042','carlog_20150809_172222','carlog_20150809_172322','carlog_20150809_172412',
             'carlog_20150809_172455','carlog_20150809_172550','carlog_20150809_172646','carlog_20150809_224506']
    #files = ['carlog_20150811_082327']
    files = ['data/navigation_calibration/'+f+'.csv' for f in files]


    data = process_df(readfromfiles(files))

    rf = ensemble.RandomForestClassifier(random_state=3); rf.min_samples_leaf = 1; rf.n_estimators=10
    X = data[['x','y','z']+ ['x5','y5','z5']]
    y = data.reset_index()['action']

    m = Model.fit_create(rf, X, y)
    m.dump('models/rover_calibration.pkl')


def train_model(df, model):
    X = df[['x', 'y', 'z', 'x5', 'y5', 'z5']]               # train set
    y = df.reset_index()['action']                          # target
    files = df.set_index()['files'].unique().tolist()       # files used for train the model

    scores = []
    for i in range(len(files)):
        itr = X.reset_index()['fname'].values == files[i]; icv = -itr
        model = model.fit(X[itr],y[itr])
        x1 = X[icv].groupby(level=['seq','action']).apply(lambda x: model.labels[model.predict_proba(x).sum(axis=0).argmax()])
        scores.append((x1.reset_index()[0]==x1.action).mean())

    return model.fit(X,y)
