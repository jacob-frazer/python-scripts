# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 18:14:41 2020

@author: Jake Frazer
"""

# building a gradient boosting decision tree using sklearn -ooooo

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import GradientBoostingClassifier

colNames = ['buying','maint','doors','seats','lug_boat','safety','classification']
data = pd.read_csv('C:\Programming\ml_data\car\car.data', header=None, names=colNames)


# manipulate data to appropriate form - turn categories into values for tree   (strings to 0,1,2 etc)
manip_data = data.copy()
manip_data['buying'] = data.buying.astype('category').cat.codes
manip_data['maint'] = data.maint.astype('category').cat.codes
manip_data['doors'] = data.doors.astype('category').cat.codes
manip_data['seats'] = data.seats.astype('category').cat.codes
manip_data['lug_boat'] = data.lug_boat.astype('category').cat.codes
manip_data['safety'] = data.safety.astype('category').cat.codes
manip_data['classification'] = data.classification.astype('category').cat.codes


# split into train and test data - 60/40
p60 = int(manip_data.shape[0]*0.6)

train = manip_data.iloc[:p60, :]
test = manip_data.iloc[p60:, :]


# scale the data (makes all lie between 0 and 1) - don't think this is necessary since all mine is categorical?
scaler = MinMaxScaler()
train = scaler.fit_transform(train)
test = scaler.transform(test)

# random state (seed)
state = 12  

# percentage of data for testing on
test_size = 0.30  
  
# split data into x - features and y - classification and split into random train test subsets (used for different learning rates)
x_train = train[['buying','maint','doors','seats','lug_boat','safety']]
y_train = train[['classification']]
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=test_size, random_state=state)


# set different learning rates
lr_list = [0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1]

for learning_rate in lr_list:
    gb_clf = GradientBoostingClassifier(n_estimators=20, learning_rate=learning_rate, max_features=2, max_depth=2, random_state=0)
    gb_clf.fit(x_train, y_train)

    print("Learning rate: ", learning_rate)
    print("Accuracy score (training): {0:.3f}".format(gb_clf.score(x_train, y_train)))
    print("Accuracy score (validation): {0:.3f}".format(gb_clf.score(x_val, y_val)))
    
    
gb_clf2 = GradientBoostingClassifier(n_estimators=20, learning_rate=0.5, max_features=2, max_depth=2, random_state=0)
gb_clf2.fit(x_train, y_train)
predictions = gb_clf2.predict(x_val)

print("Confusion Matrix:")
print(confusion_matrix(y_val, predictions))

print("Classification Report")
print(classification_report(y_val, predictions))