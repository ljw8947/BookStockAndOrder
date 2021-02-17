import pandas as pd
from datetime import datetime

dataSourcePath = '数据源.xlsx'
bookNameStr = '书名'
pressStr = '出版社'
priceStr = '定价'
discountStr = '折扣'
stockStr = '库存'
ISBNStr = 'ISBN'
countStr = '数量'
commentStr = '备注'
lowestDiscountStr = '最高折扣'
highestDiscountStr = '最低折扣'
lowestDiscountVendorStr = '最高折扣供应商'
highestDiscountVendorStr = '最低折扣供应商'


class SplitMode():
    NotSplit = 1  # 优先选择库存够折扣最低的供应商


schoolType = ['小学', '初中', '高中']


def getTimeString():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def getVendorList(headers):
    vendors = []
    for header in headers:
        if not header.find(discountStr) == -1:
            vendor = header.split('_')[0]
            vendors.append(vendor)
    return vendors


def getVendorStockStr(vendor):
    return vendor+'_'+stockStr


def getVendorDiscountStr(vendor):
    return vendor+'_'+discountStr


def dataSource2Excel(dataSource, changer, path):
    dataSource.to_excel(path+'/数据源.xlsx', index=None)
    dataSource.to_excel(path+'/数据源_'+getTimeString() + '_' +
                        changer+'.xlsx', index=None)


def readVendorData(filePath):
    fileData = pd.read_excel(filePath)
    if not '库存' in fileData:
        fileData['库存'] = 0
    data = fileData[[bookNameStr, ISBNStr,
                     pressStr, priceStr, discountStr, stockStr]]
    return data


def readDataSource(filePath):
    fileData = pd.read_excel(filePath)
    return fileData


def readSchoolOrder(filePath):
    data = pd.read_excel(filePath)
    return data


def getFilePath(file):
    flag = '/'
    index = file.rfind(flag)
    path = file[0: index]
    return path


def mergeVendorData(vendorName, vendorFilePath, dataSourcePath):
    path = getFilePath(dataSourcePath)
    vendorData = readVendorData(vendorFilePath)
    dataSource = readDataSource(dataSourcePath)

    vendorStock = vendorName+'_'+stockStr
    vendorDiscount = vendorName+'_'+discountStr

    dataSource[vendorStock] = 0
    dataSource[vendorDiscount] = 0

    # tempData = readDataSource(dataSourcePath)
    tempData = dataSource.drop(index=dataSource.index)
    dataSource[vendorStock] = 0
    dataSource[vendorDiscount] = 0

    for vendorItem in vendorData.iterrows():
        vendorBook = vendorItem[1]
        exist = False
        for index, item in dataSource.iterrows():
            if item['ISBN'] == vendorBook['ISBN']:
                exist = True
                item[vendorStock] = vendorBook[stockStr]
                item[vendorDiscount] = vendorBook[discountStr]
                dataSource.iloc[index] = item
                break
        if not exist:
            new_row = {bookNameStr: vendorBook[bookNameStr], ISBNStr: vendorBook[ISBNStr],
                       pressStr: vendorBook[pressStr], priceStr: vendorBook[priceStr],
                       vendorStock: vendorBook[stockStr], vendorDiscount: vendorBook[discountStr]}
            tempData = tempData.append(new_row, ignore_index=True)
    dataSource = dataSource.append(tempData, ignore_index=True)
    dataSource2Excel(dataSource, vendorName, path)


def mergeMultiVendorsData(vendorFiles, dataSourcePath):
    for vendorFile in vendorFiles:
        vendor = vendorFile.split('.')[0].split('/').pop()
        mergeVendorData(vendor, vendorFile, dataSourcePath)
    return True


def splitSchoolOrder(schoolName, orderFilePath, dataSourcePath,
                     mode=SplitMode.NotSplit):
    path = getFilePath(dataSourcePath)
    schoolData = readSchoolOrder(orderFilePath)
    dataSource = readDataSource(dataSourcePath)
    vendorDict = {}
    vendorList = getVendorList(dataSource.columns.tolist())
    for vendor in vendorList:
        vendorDict[vendor] = schoolData.drop(index=schoolData.index)
        vendorDict[vendor][discountStr] = 0

    notFound = schoolData.drop(index=schoolData.index)
    notFound[commentStr] = ''

    for schoolIndex, order in schoolData.iterrows():
        if order[countStr] == 0 or pd.isnull(order[countStr]):
            continue

        for sourceIndex, source in dataSource.iterrows():
            if not order[ISBNStr] == source[ISBNStr]:
                continue

            finalVendor = ''
            for vendor in vendorList:
                if source[vendor+'_'+stockStr] >= order[countStr]:
                    if finalVendor == '':
                        finalVendor = vendor
                    if source[vendor+'_'+discountStr] < source[finalVendor+'_'+discountStr]:
                        finalVendor = vendor
            if not finalVendor == '':
                order[discountStr] = source[finalVendor+'_'+discountStr]
                source[finalVendor+'_'+stockStr] = source[finalVendor +
                                                          '_'+stockStr] - order[countStr]
                dataSource.iloc[sourceIndex] = source
                vendorDict[finalVendor] = vendorDict[finalVendor].append(
                    order, ignore_index=True)
            else:
                order[commentStr] = '没有库存充足的供应商'
                notFound = notFound.append(order, ignore_index=True)

    time = getTimeString()
    if not notFound.empty:
        notFound.to_excel(path+'/'+schoolName + '_库存不足_' +
                          time+'.xlsx', index=None)

    vendorOrders = vendorDict.items()
    for vendor, order in vendorOrders:
        if not order.empty:
            order.to_excel(path+'/'+schoolName + '_' +
                           vendor+'_'+time+'.xlsx', index=None)

    dataSource2Excel(dataSource, schoolName, path)

    return True


def generateSchoolSupplyList(schoolName, schoolTypes, copyCount, dataSourcePath=dataSourcePath):
    path = getFilePath(dataSourcePath)

    dataSource = readDataSource(dataSourcePath)
    vendorList = getVendorList(dataSource.columns.tolist())

    dataSource[countStr] = copyCount
    dataSource[lowestDiscountVendorStr] = ''
    dataSource[lowestDiscountStr] = 0
    dataSource[highestDiscountVendorStr] = ''
    dataSource[highestDiscountStr] = 0

    dropRows = []
    for index, item in dataSource.iterrows():
        isRightType = False
        for type in schoolTypes:
            if item[type] == 1:
                isRightType = True
                break

        if not isRightType:
            dropRows.append(index)
            continue

        lowestVendor = ''
        hightestVendor = ''
        for vendor in vendorList:
            if item[getVendorStockStr(vendor)] < copyCount or pd.isnull(item[getVendorStockStr(vendor)]):
                continue
            if lowestVendor == '':
                lowestVendor = vendor
            else:
                if item[getVendorDiscountStr(lowestVendor)] > item[getVendorDiscountStr(vendor)]:
                    lowestVendor = vendor
            if hightestVendor == '':
                hightestVendor = vendor
            else:
                if item[getVendorDiscountStr(hightestVendor)] < item[getVendorDiscountStr(vendor)]:
                    hightestVendor = vendor
        if lowestVendor == '':
            dropRows.append(index)
            continue

        item[lowestDiscountVendorStr] = lowestVendor
        item[lowestDiscountStr] = item[getVendorDiscountStr(lowestVendor)]
        item[highestDiscountVendorStr] = hightestVendor
        item[highestDiscountStr] = item[getVendorDiscountStr(hightestVendor)]
        dataSource.iloc[index] = item

    for vendor in vendorList:
        del dataSource[getVendorDiscountStr(vendor)]
        del dataSource[getVendorStockStr(vendor)]

    dataSource = dataSource.drop(dropRows)

    dataSource.to_excel(path+'/学校书目_'+schoolName + '_' +
                        getTimeString() + '.xlsx', index=None)
    return True


# mergeVendorData('供应商3', '供应商.xlsx')
# splitSchoolOrder('啦啦小学', '学校订单.xlsx')
# generateSchoolSupplyList('啦啦小学', [SchoolType.primarySchool], 3)
print(type(1))
