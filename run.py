import os
import json
import torch
import pickle
import numpy as np
import pandas as pd
import torch.nn as nn
import torch.optim as optim
from datetime import datetime
from copy import deepcopy as dc
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from read_data_fromTB import AI_Elec_Get
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
osSystem = 'windows' # 'linux'

phase=os.getenv('PHASE')
buldingname=os.getenv('buldingname')
if  phase == None:
    phase='train'
if  buldingname == None:
    buldingname='23_Aboreyhan_1'

device=torch.device("cuda" if torch.cuda.is_available() else "cpu")

# if osSystem == 'windows':
#     folder=r'C:\Users\Public.DESKTOP-J6Q3U28\Desktop\lstm1_final'
# else:
#     folder= '/home/n/Desktop/lstm1_final'

# It is better practice to do this, -->  Greate, but above code is faster due to runnig without any lib, and this path is constant in the server forever!
folder = os.path.dirname(os.path.abspath(__file__))
# print(f"\n Da folder Path: {folder}")


now=datetime.now()  
savename=f'{now.strftime("%Y_%m_%d__%H_%M_%S")}'    

if osSystem == 'windows' :
    data=f'{folder}\Database\{buldingname}.pkl'
else :
    data=f"{folder}/Database/{buldingname}.pkl"

# try :
#     df=pd.read_pickle(data)[['datetime', 'compensation']]
# except : 
df = pd.DataFrame(columns=['datetime', 'epoch_time', 'value', 'compensation'])
df.set_index("datetime",inplace=True)
df_pikle =  pd.read_pickle(data)
if len(df_pikle)>1 :
    df = pd.concat([df,df_pikle], axis=0).iloc[:-1, :]

print(f"\n\n The concated df at the first is this asdadadasd\n {df}\nThe typ")

# df.set_index('datetime', inplace=True)   
# print(f"\n\n The concated df at the first is this after set index\n {df}")

lastdata=df.index.max()
print(lastdata)

#########<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< اینجا رو با کد گرفتن از اب پی آی جلیگزین کن>>>>>>>>>>>>>>>>>
df_new = AI_Elec_Get(meter_kind='electricity',meter_name=buldingname,
            start_time= lastdata ,
            stop_time= now.strftime("%Y-%m-%d %H:%M:%S"))

print(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n{df_new}\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
win_size_1 = 1
win_size_2 = 24
df_new['value'] = pd.to_numeric(df_new['value'], errors='coerce')
df_new['processed_value'] = df_new['value'].copy()
Q1 = df_new['processed_value'].quantile(0.25)
Q3 = df_new['processed_value'].quantile(0.75)
IQR = Q3 - Q1
threshold = 1.5 * IQR
outliers = df_new[(df_new['processed_value'] < (Q1 - threshold)) | (df_new['processed_value'] > (Q3 + threshold))]
df_new['processed_value'] = df_new['processed_value'].apply(
    lambda x: np.nan if x in outliers['processed_value'].values else x)
df_new['processed_value_interpolated'] = df_new['processed_value'].interpolate(method='linear', limit_direction='forward', limit=1)   # interpolate_limit_sample = 1
rolling_mean = df_new['processed_value_interpolated'].rolling(window=win_size_1, center=True).mean()
rolling_mean.ffill(inplace=True)
rolling_mean.bfill(inplace=True)
df_new['processed_value_rolling'] = rolling_mean
df_new['hourly_diff'] = df_new['processed_value_rolling'].diff()
df_new.loc[0, 'hourly_diff'] = df_new['processed_value_rolling'].iloc[0]
Q1_hourly = df_new['hourly_diff'].quantile(0.25)
Q3_hourly = df_new['hourly_diff'].quantile(0.75)
IQR_hourly = Q3_hourly - Q1_hourly
threshold_hourly = 1.5 * IQR_hourly
outliers_hourly = df_new[(df_new['hourly_diff'] < (Q1_hourly - threshold_hourly)) | (df_new['hourly_diff'] > (Q3_hourly + threshold_hourly))]
df_new['hourly_diff'] = df_new['hourly_diff'].apply(
    lambda x: 0 if x in outliers_hourly['hourly_diff'].values else x)
normal_values = df_new[(df_new['hourly_diff'] >= (Q1_hourly - threshold_hourly)) & (df_new['hourly_diff'] <= (Q3_hourly + threshold_hourly)) & (df_new['hourly_diff']>0)]
mean_normal_values = normal_values['hourly_diff'].mean()
df_new['hourly_filled_zero'] = df_new['hourly_diff'].fillna(0)
rolling_mean = df_new['hourly_filled_zero'].rolling(window=win_size_2, center=True).mean()
rolling_mean.ffill(inplace=True)
rolling_mean.bfill(inplace=True)
df_new['hourly_soft'] = df_new.apply(
    lambda row: (
        rolling_mean[row.name] if row['hourly_filled_zero'] == 0 and rolling_mean[row.name] != 0
        else mean_normal_values if row['hourly_filled_zero'] == 0 and rolling_mean[row.name] == 0
        else row['hourly_filled_zero']
    ),
    axis=1
)
print(100*'*/')
print(df_new.index[-1],'_______\n', lastdata)


print('\n\n\n\n\n\n\n\n\n')
print(100* '*')
print(100* '*')
print("THIS IS df_new:")
print(df_new)


df_new = df_new.loc[:, [ 'epoch_time', 'value', 'hourly_diff', 'hourly_filled_zero', 'hourly_soft']]

print('\n\n\n\n\n\n\n\n\n')
print(100* '*')
print(100* '*')
print("THIS IS df_new:afterrrrrrrrrrrrr")
print( df_new)


df_new.columns = [ 'epoch_time', 'value', 'hourly_value', 'compensation', 'hourly_soft']
df_save = df_new[[ 'epoch_time', 'value', 'compensation']].copy()

# df_new_filtered = df_new[df_new.index[-1] > lastdata]
# if len(df_save)>1 :
df_combined = pd.concat([df, df_save], axis=0)
df=df_combined.copy()
df_combined.to_pickle(data)
df_combined['compensation'] = df_combined['compensation'].fillna(0)
df_combined = df_combined.reset_index() 
df_combined = df_combined.iloc[:-1, :]
df = df_combined[['datetime', 'compensation']]
df = df.rename(columns={'datetime': 'Date', 'compensation': 'compensation'}).fillna(0)
df = df[['Date', 'compensation']]
df = df.set_index("Date")


print('\n\n\n\n\n\n\n\n\n')
print(100* '%')
print(100* '%%')
print("THIS IS df_combined:")
# print(df_combined)
print(df['compensation'].info())



# Model
class LSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers):
        super().__init__()
        self.hidden_dim=hidden_dim
        self.num_layers=num_layers

        self.lstm=nn.LSTM(input_dim, hidden_dim, num_layers,
                            batch_first=True)

        self.fc=nn.Linear(hidden_dim, 1)

    def forward(self, x):
        batch_size=x.size(0)
        h0=torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device)
        c0=torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device)

        out, _=self.lstm(x, (h0, c0))
        out=self.fc(out[:, -1, :])
        return out
model=LSTM(input_dim=1, hidden_dim=4,  num_layers=1)
optimizer=torch.optim.Adam(model.parameters(), lr=0.01) 
loss_function=nn.MSELoss()

class dataofdf(Dataset):
    def __init__(self, X, y):
        self.X=X
        self.y=y
    def __len__(self):
        return len(self.X)
    def __getitem__(self, i):
        return self.X[i], self.y[i]

num_epochs=75
batch_size=16
# Train
if phase=='train':  
    dfnew=dc(df)
    dfnew['compensation']=dfnew['compensation'] 
    for i in range(1, 25):
        dfnew[f'compensation(t-{i})']=dfnew['compensation'].shift(i)
    dfnew.dropna(inplace=True)    
    dfnew=dfnew.to_numpy()
    split_index=int(dfnew.shape[0] * 0.8+1)
    trainpart= dfnew[:split_index]
    testpart=dfnew[split_index:]
    scaler= MinMaxScaler(feature_range=(-1, 1))
    trainpart=scaler.fit_transform(trainpart)
    testpart=scaler.transform(testpart)
    newdf=np.concatenate([trainpart, testpart], axis=0)
    X=newdf[:, 1:]
    y=newdf[:, 0]
    xtrain=X[:split_index]
    xtest=X[split_index:]
    ytrain=y[:split_index]
    ytest=y[split_index:]
    xtrain=xtrain.reshape((-1, 24, 1))
    xtest=xtest.reshape((-1, 24, 1))
    ytrain=ytrain.reshape((-1, 1))
    ytest=ytest.reshape((-1, 1))
    xtrain=torch.tensor(xtrain).float()
    ytrain=torch.tensor(ytrain).float()
    xtest=torch.tensor(xtest).float()
    ytest=torch.tensor(ytest).float()
    traindata=dataofdf(xtrain, ytrain)
    testdata=dataofdf(xtest, ytest)
    datatrain=DataLoader(traindata, batch_size=batch_size, shuffle=True)
    datatest=DataLoader(testdata, batch_size=batch_size, shuffle=False)
    bestlossval=float('inf')
    trainlosses=[] 
    vallosses=[]    
    allofdata=[]  
    if osSystem == 'windows' :
        data=f'{folder}\Models\{buldingname}'    
    else :
        data=f'{folder}/Models/{buldingname}' 
    mymodels=[f for f in os.listdir(data) if f.endswith('.pkl')]
    bestfile=None
    bestmae=float('inf')
    for file in mymodels:
        filemae=float(file.split('_loss_')[1].split('.pkl')[0])  
        if filemae<bestmae:
            bestmae=filemae
            bestfile=file
    if bestfile:
        if osSystem == 'windows' :
            buldingmodel=f'{folder}\Models\{buldingname}'
        else :
            buldingmodel=f'{folder}/Models/{buldingname}'
        with open(os.path.join(buldingmodel, bestfile), 'rb') as f:
            model=pickle.load(f)
        if model is not None:
            model.load_state_dict(model.state_dict())
        else:
            pass
    for epoch in range(num_epochs):
        model.train(True)
        runnigloss=0.0
        for i, batch in enumerate(datatrain):
            xdata, ydata=batch[0].to(device), batch[1].to(device)
            loss=loss_function(model(xdata), ydata)
            runnigloss+=loss.item()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if i%100 ==99:  
                trainloss=runnigloss/100
                runnigloss=0.0
        # print()
        trainloss1=loss.item()                 
        trainlosses.append(trainloss1) 
        model.eval() 
        runnigloss=0.0
        allofdata=[] 
        with torch.no_grad():  
            for i,batch in enumerate(datatest):
                xdata, ydata=batch[0].to(device), batch[1].to(device)
                loss=loss_function(model(xdata), ydata)
                runnigloss+=loss.item()
                allofdata.append(model(xdata).cpu().numpy())
        validloss=runnigloss/len(datatest)
        vallosses.append(runnigloss/len(datatest)) 
        allofdata.extend(np.concatenate(allofdata)) 
        if validloss<bestlossval:
            bestlossval=validloss
            model_name=f'bestmodel_{buldingname}_loss_{validloss:.4f}.pkl'
            if osSystem == 'windows' :
                buldingmodel=f'{folder}\Models\{buldingname}'
            else :
                buldingmodel=f'{folder}/Models/{buldingname}'             
            model_filepath=os.path.join(buldingmodel, model_name)
            if osSystem == 'windows' :
                data=f'{folder}\Models\{buldingname}'    
            else :
                data=f'{folder}/Models/{buldingname}' 
            mymodels=[f for f in os.listdir(data) if f.endswith('.pkl')]
            bestfile=None
            bestmae=float('inf')

            for file in mymodels:
                filemae=float(file.split('_loss_')[1].split('.pkl')[0])  
                if filemae<bestmae:
                    bestmae=filemae
                    bestfile=file
            if validloss<bestmae:
                with open(model_filepath, 'wb') as f:
                    pickle.dump(model, f)
            else:
                pass
            if osSystem == 'windows' :
                fileresultfold=f'{folder}\Results\{buldingname}\{buldingname}.txt'
            else :
                fileresultfold=f'{folder}\Results\{buldingname}\{buldingname}.txt'
            fileresult1=[]
            fileresult1.append("\n#" + "=" * 100)
            fileresult1.append(f"Trning strated at :{savename}")
            fileresult1.append(f'trainlosses={trainlosses} ,vallosses={vallosses}')
            fileresult1.append(str(model))  
            fileresult1.append(f'Number of parameters: {sum(p.numel() for p in model.parameters())}') 
            with open(fileresultfold, 'a') as f: 
                f.write('\n'.join(fileresult1) + '\n\n')   
        else:
            pass    
    model.eval()  
    allofdata=[]
    with torch.no_grad():
        for batch in datatest:
            xdata=batch[0].to(device)
            allofdata.append(model(xdata).cpu().numpy())  
            predictions1=np.concatenate(allofdata)    
    predictions2=np.zeros((predictions1.shape[0], 25)) 
    predictions2[:, 0]=predictions1.flatten()  
    predictions2=scaler.inverse_transform(predictions2)      
    lastdata= predictions2[:, 0]
    if osSystem == 'windows' :
        jsonresults=f'{folder}\Results\{buldingname}\{buldingname}.json'
    else :
        jsonresults=f'{folder}/Results/{buldingname}/{buldingname}.json'   
    with open(jsonresults, 'w') as f:
        json.dump(lastdata.tolist(), f)
else:
    dfnew=dc(df)
    dfnew['compensation']=dfnew['compensation'] 
    for i in range(1, 25):
        dfnew[f'compensation(t-{i})']=dfnew['compensation'].shift(i)
    dfnew.dropna(inplace=True)    
    newdf=dfnew.to_numpy()
    scaler=MinMaxScaler(feature_range=(-1, 1))
    newdf=scaler.fit_transform(newdf)
    X=newdf[:, 1:]  
    y=newdf[:, 0]  
    X=X.reshape((-1, 24, 1))
    y=y.reshape((-1, 1))
    X=torch.tensor(X).float()
    y=torch.tensor(y).float()
    X=X[-1:, :]   
    datanew2=pd.date_range(start=lastdata, periods=24, freq='h')
    datedf=pd.DataFrame({'Date': datanew2})
    if osSystem == 'windows':
        data=f'{folder}\Models\{buldingname}'    
    else:
        data=f'{folder}/Models/{buldingname}'
    mymodels=[f for f in os.listdir(data) if f.endswith('.pkl')]
    bestfile=None
    bestmae=float('inf')
    for file in mymodels:
        try:
            filemae=float(file.split('_loss_')[1].split('.pkl')[0])  
            if filemae<bestmae:
                bestmae=filemae
                bestfile=file
        except (IndexError, ValueError) as e:
            pass 
    if bestfile:
        if osSystem == 'windows' :
            modelfold=f'{folder}\Models\{buldingname}'
        else :
            modelfold=f'{folder}/Models/{buldingname}'        
        with open(os.path.join(modelfold, bestfile), 'rb') as f:
            model=pickle.load(f)           
    matrix=torch.zeros(24, 24, 1)
    matrix[:1, :, :]=dc(X[-1:, :, :])
    alldata=[]
    for i in range(1, 23):
        matrix2=matrix[i - 1]
        data=model(matrix2.unsqueeze(0))
        datas=torch.cat((matrix2[1:], torch.zeros(1, matrix2.size(1))))
        datas[23]=data.squeeze()
        alldata.append(data.detach().numpy().squeeze())
        matrix[i]=datas   
    datas=model(matrix.to(device)).detach().cpu().numpy().flatten()
    matrix_new=np.zeros((matrix.shape[0], 25))
    matrix_new[:, 0]=datas
    matrix_new=scaler.inverse_transform(matrix_new)
    lastdata=dc(matrix_new[:, 0])
    if osSystem == 'windows' :
        jsonresults=f'{folder}\Results\{buldingname}\{buldingname}.json'
    else :
        jsonresults=f'{folder}/Results/{buldingname}/{buldingname}.json'   
    with open(jsonresults, 'w') as f:
        json.dump(lastdata.tolist(), f)
        
        




    

