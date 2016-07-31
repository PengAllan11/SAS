#encoding: utf-8

from flask import Flask,url_for
import MySQLdb
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn import preprocessing
from sklearn.preprocessing import LabelBinarizer
from sklearn.externals.six import StringIO
from sklearn import tree
from flask import request

app = Flask(__name__)


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

if __name__ == '__main__':
    app.run()
