#encoding: utf-8

from flask import Flask,url_for
import MySQLdb
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn import tree
from sklearn.cross_validation import train_test_split
from flask import request

app = Flask(__name__)

def get_mysql_data(sql):
#    ip_address=str(input('Please enter the MySQL IP Address:'))
#    user_name=input('Please enter the MySQl user name:')
#    password=input('Please enter the MySQL password: ')
#    database_name=input('Please enter the MySQL database name: ')
#    db=MySQLdb.connect(ip_address,user_name,password,database_name)
    db=MySQLdb.connect("10.60.38.159","admin","1234","SAS")
    cursor=db.cursor()
    try:
        cursor.execute(sql)
        results=cursor.fetchall()
    except:
        print 'Error:unable to fecth data.'
#将数据转化成DataFrame形式
    data=pd.DataFrame([j for j in i] for i in results)
#属性值命名
    data.rename(columns={0:'XBMC',1: 'MZMC', 2: 'JGMC', 3: 'CSRQ', \
    4: 'WHCDMC',5:'HYZKMC',6:'ZZMMMC',7:'SFMC',8:'SWCS',9:'WZCS',\
    10:'LGCS',11:'ISBAD'}, inplace=True)
    return data

#将数据转化为list类型，再转化为0-1表示的数组
def __to_list(data):
    list_data=[]
    list_data=data.to_dict(orient='records')
    vec=DictVectorizer()
    data1=vec.fit_transform(list_data).toarray()
    return data1

#计算模型准确率
def score(x_predict,x_real):
    n=0.0
    k=0.0
    score=0
    for i in x_predict:
        n=n+1
        for j in x_real:
            if i.all()==j.all():
                k=k+1
    score=k/n
    return score


#获取实验数据
def get_all_data():
    data_set=get_mysql_data('select * from property_data limit 10000')
    #训练集中因子的获取,并转化为list类型
    X_data=data_set.iloc[:,0:11]
    X_data=__to_list(X_data)

    #训练集中label的获取,并转化为list类型
    Y_data=data_set.iloc[:,11:12]
    Y_data=__to_list(Y_data)
    return X_data,Y_data


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/SAS')
def index():
    num = request.args.get('num')
    print num
    db = MySQLdb.connect("10.60.38.159", "admin", "1234", "SAS",)
    cursor = db.cursor()
    sql = "select * from property_data limit 10000"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except:
        print "Error:unable to fecth data."

    # 将数据转化成DataFrame形式
    data = pd.DataFrame([[j for j in i] for i in results])
    # type = sys.getfilesystemencoding()
    # data.decode('utf-8').encode(type)
    # 属性值命名
    data.rename(columns={0: 'XBMC', 1: 'MZMC', 2: 'JGMC', 3: 'CSRQ', \
                         4: 'WHCDMC', 5: 'HYZKMC', 6: 'ZZMMMC', 7: 'SFMC', 8: 'SWCS', 9: 'WZCS', \
                         10: 'LGCS', 11: 'ISBAD'}, inplace=True)
    # print df.head()


    # 测试集中因子的获取,并转化为list类型
    X_train = data.iloc[:, 0:11]
    # print df1
    features_list = []
    features_list = X_train.to_dict(orient='records')
    # 将list转化为0-1表示的数组
    vec = DictVectorizer()
    dummy_X = vec.fit_transform(features_list).toarray()
    names = vec.get_feature_names()
    # print('dummy_X:'+str(dummy_X))
    # print names


    # 测试集中label的获取,并转化为list类型
    Y_train = data.iloc[:, 11:12]
    label_list = Y_train.to_dict(orient='records')
    dummy_Y = vec.fit_transform(label_list).toarray()
    # print('label_list:'+str(label_list))

    # 测试集
    test_sql = "select * from property_data limit 1000,50"

    try:
        cursor.execute(test_sql)
        results = cursor.fetchall()
    except:
        print "Error:unable to fecth TEST data."

    # peng an adds
    # print results
    # 将数据转化成DataFrame形式
    test_data = pd.DataFrame([[j for j in i] for i in results])
    # 属性值命名
    test_data.rename(columns={0: 'XBMC', 1: 'MZMC', 2: 'JGMC', 3: 'CSRQ', \
                              4: 'WHCDMC', 5: 'HYZKMC', 6: 'ZZMMMC', 7: 'SFMC', 8: 'SWCS', 9: 'WZCS', \
                              10: 'LGCS', 11: 'ISBAD'}, inplace=True)
    # 测试集中因子的获取,并转化为list类型
    X_test = data.iloc[:, 0:11]
    # print df1
    features_list = []
    features_list = X_test.to_dict(orient='records')
    # 将list转化为0-1表示的数组
    vec = DictVectorizer()
    test_X = vec.fit_transform(features_list).toarray()
    names = vec.get_feature_names()
    # print('dummy_X:'+str(dummy_X))
    # 测试集中label的获取,并转化为list类型
    Y_test = data.iloc[:, 11:12]
    label_list = Y_test.to_dict(orient='records')
    test_Y = vec.fit_transform(label_list).toarray()
    # print('label_list:'+str(label_list))

    # 调用sklearn中的决策树算法,模型的生成与准确率的验证
    clf = tree.DecisionTreeClassifier(criterion='entropy')  # ID3,默认cart
    clf = clf.fit(dummy_X, dummy_Y)
    print('clf:' + str(clf))
    with open('tree.dot', 'w') as f:
        f = tree.export_graphviz(clf, out_file=f, feature_names=names)
    score = clf.score(test_X, test_Y)
    print score

    # num = int(input('Please enter what you want to predict(enter a number): '))
    num = int(num)
    # print X_train[num,:]
    one_row_X = dummy_X[num:num +1, :]
    print ('one_row_X:' + str(one_row_X))
    predictedY = clf.predict(one_row_X)
    # print predictedY
    # predicted=[]
    # print X_train
    # for X in X_train:
    returnout = ''
    for x in predictedY:
        # print X
        if x[0] == 1:
            print x, '  good'
            returnout = '准确率：' + str(score) + '\n第' + str(num) + '个人：' +"good"
        else:
            print x, '  bad'
            returnout = '准确率：' + str(score) + '\n第' + str(num) + '个人：' +"bad"

    return returnout

@app.route('/decision_tree')
def decision_tree():
    x_data, y_data = get_all_data()
    X_train, X_test, Y_train, Y_test = train_test_split(x_data, y_data, test_size=0.2)
    predict_set = get_mysql_data('select * from property_data limit 10000')
    # 训练集中因子的获取,并转化为list类型
    X_predict = predict_set.iloc[:, 0:11]
    X_predict = __to_list(X_predict)

    # 训练集中label的获取,并转化为list类型
    Y_predict = predict_set.iloc[:, 11:12]

    # 调用sklearn中的决策树算法,模型的生成与准确率的验证
    clf = tree.DecisionTreeClassifier(criterion='entropy')  # ID3,默认cart
    clf.fit(X_train, Y_train)
    print 'clf:' + str(clf)
    ##将此模型的决策树直接生成
    # with open('tree.dot','w') as f:
    #    f=tree.export_graphviz(clf,out_file=f,feature_names=names)
    predict_score = clf.score(X_test, Y_test)
    print '准确率为', predict_score

    # 预测过程
    # 准确率的计算
    # X_test=X_test[:,:]
    # Y_test_predict=clf.predict(X_test)
    # score=score(Y_test_predict,Y_test)
    # print '准确率为： ',score
    # for i in range(10):
    #    print Y_test

    # 预测给定值的label
    # num=int(input('Please enter what you want to predict(enter a number): '))
    # print X_train[num,num+100:]
    one_row_X = X_predict[20:40, :]
    # print Y_predict[20:40,:]
    # for column in Y_predict[20:40,:]:
    #    print column[11]
    # print ('one_row_X:'+str(one_row_X))
    predictedY = clf.predict(one_row_X)
    # print predictedY
    # predicted=[]
    # print X_train
    # for X in X_train:
    returnData = []

    for x in predictedY:
        # print X
        if x[0] == 1:
            # print x,'  good'
            returnData.append({"ISBAD": "good"})
        else:
            # print x,'  bad'
            returnData.append({"ISBAD": "bad"})
    # print(clf.feature_importances_)
    # print clf.predict_proba(one_row_X)
    i = 0
    for value in clf.predict_proba(one_row_X)[1]:
        returnData[i]["rate"] = value[0]
        i = i + 1
        # print value[0]

    for pair in returnData:
        print pair

    return str(returnData)


if __name__ == '__main__':
    app.run()

