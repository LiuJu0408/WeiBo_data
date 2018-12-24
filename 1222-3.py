#coding=utf-8
#create by LiuJu
import os,sys
from osgeo import gdal,ogr,osr
import pandas as pd
import numpy
ogr.UseExceptions()  #报错机制
gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8","NO")  #为了支持中文路径
gdal.SetConfigOption("SHAPE_ENCODING","CP936")  #为了使属性表字段支持中文
ogr.RegisterAll()  #注册所有的驱动 
Weibo_data = pd.DataFrame()
def readShap():
    global Weibo_data
    fn = r"G:\\Weibo\\bj.gdb" #输入shp文件
    ds = ogr.Open(fn,0)
    if ds is None:
        sys.exit('could not open{0}.'.format(fn))
    lyr = ds.GetLayer(0)
    i = 0
    ID = []
    USER_ID = []
    longtitude_G = []
    latitude_G = []
    longtitude_P =[]
    latitude_P =[]
    PubTime = []
    Tools =[]
    text = []
    print('Start read')
    for feat in lyr:
        if feat.GetField('PubTime')[5:7] not in ['01','02','12']:#避免过年信息的干扰
            ID.append(i)
            USER_ID.append(feat.GetField('ID'))
            longtitude_G.append(feat.GetField('Co_oridinate2'))
            latitude_G.append(feat.GetField('Co_oridinate1'))
            longtitude_P.append(feat.GetField('X'))
            latitude_P.append(feat.GetField('Y'))
            PubTime.append(feat.GetField('PubTime'))
            Tools.append(feat.GetField('Tools'))
            Content = feat.GetField('Content')
            Content1 = Content.encode('utf-8') #bytes类型
            Content2 = Content1.decode('utf-8') #str类型
            Content3 = Content2.encode('gbk','ignore') #bytes类型
            text.append(Content3.decode('gbk','ignore')) #str类型
            i += 1
            print(i)
            #if i == 100:
                #break
    print('End read')
    del ds
    Weibo_dict = {
        'ID':ID,
        'USER_ID':USER_ID,
        'longtitude_G':longtitude_G,
        'latitude_G':latitude_G,
        'longtitude_P':longtitude_P,
        'latitude_P':latitude_P,
        'PubTime':PubTime,
        'Tools':Tools,
        'text':text
    }
    Weibo_frame1 = pd.DataFrame(Weibo_dict,columns=['ID','USER_ID','longtitude_G','latitude_G','longtitude_P','latitude_P','PubTime','Tools','text'])
    print('Start Duplicate')
    Weibo_data = Weibo_frame1.drop_duplicates(subset=['text'],keep=False)
    print('Complete Duplicate')

#创建shap文件
def createShap():
    global Weibo_data
    driver = ogr.GetDriverByName('ESRI Shapefile')  #数据格式的驱动
    outfile = r"G:\\Weibo\\temp" #输出shp路径
    outname = "bj17_1" #输出shp名称
    outshp = outfile + "\\"+outname+".shp"
    outprj = outfile + "\\"+outname+".prj"
    if not os.path.exists(outfile):
        os.makedirs(outfile) 
    if os.access(outshp,os.F_OK):
        driver.DeleteDataSource(outshp)
    ds = driver.CreateDataSource(outfile)
    shapLayer = ds.CreateLayer(outname,geom_type=ogr.wkbPoint);
    #指定投影
    sr = osr.SpatialReference();
    sr.ImportFromEPSG(32612);
    prjFile = open(outprj,'w');
    sr.MorphToESRI();
    prjFile.write(sr.ExportToWkt());
    prjFile.close();
    #添加字段
    fieldDefn = ogr.FieldDefn('USER_ID', ogr.OFTString) 
    fieldDefn.SetWidth(8)
    shapLayer.CreateField(fieldDefn)

    fieldDefn.SetName('Text')
    fieldDefn.SetWidth(64)
    shapLayer.CreateField(fieldDefn)

    for field in ['PubTime','Tools']:
        fieldDefn.SetName(field)
        shapLayer.CreateField(fieldDefn)

    for field in ['longG','laG','longP','laP']:
        fieldDefn.SetName(field)
        fieldDefn.SetType(ogr.OFTReal)
        fieldDefn.SetPrecision(4)
        shapLayer.CreateField(fieldDefn)
    #创建要素
    defn = shapLayer.GetLayerDefn()
    feature = ogr.Feature(defn);
    Weibo_length = len(Weibo_data)
    for i in range(Weibo_length):
        try:
            feature.SetField("USER_ID",Weibo_data['USER_ID'][i]) #字段值
            feature.SetField("longG",Weibo_data['longtitude_G'][i]) #字段值
            feature.SetField("laG",Weibo_data['latitude_G'][i]) #字段值
            feature.SetField("longP",Weibo_data['longtitude_P'][i]) #字段值
            feature.SetField("laP",Weibo_data['latitude_P'][i]) #字段值
            feature.SetField("PubTime",Weibo_data['PubTime'][i]) #字段值
            feature.SetField("Tools",Weibo_data['Tools'][i]) #字段值
            feature.SetField("Text",Weibo_data['text'][i]) #字段值
            #添加要素
            point = ogr.Geometry(ogr.wkbPoint) 
            point.AddPoint(float(Weibo_data['longtitude_G'][i]),float(Weibo_data['latitude_G'][i]))
            feature.SetGeometry(point);
            shapLayer.CreateFeature(feature)
        except:
            pass
        print(i)
    feature.Destroy()
    ds.Destroy()

def ShpToJson():
    Shpfile = 'G:\\Zhongqi\\shp\\subway.shp' #原始shp文件
    Jsonfile = 'G:\\Weibo\\temp\\bj17_1.json' #目标JSON文件
    command = 'ogr2ogr -f "GeoJSON" '+ Jsonfile +' '+ Shpfile #shp转化为json
    #command = 'ogr2ogr -lco encoding=UTF-8 -f "ESRI Shapefile" ' + Shpfile + ' ' + Jsonfile #json转化为shp,“-lco encoding=UTF-8”防止乱码
    os.popen(command)
if __name__ == "__main__":
    #readShap() #读取shp文件
    #createShap() #创建新的shp文件
    ShpToJson() #将shp文件转化为json文件
