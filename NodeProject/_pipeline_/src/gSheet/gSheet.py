import gspread,csv,os
from oauth2client.service_account import ServiceAccountCredentials

rootPath = os.path.dirname(os.path.abspath(__file__))
jsonKeyPath = rootPath + '/899435123a5b_production.json'
sheetName = 'AnimTracking_Template'

def getSheetName():
    global sheetName
    return sheetName

def connect(*_):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credential = ServiceAccountCredentials.from_json_keyfile_name(jsonKeyPath, scope)
    gc = gspread.authorize(credential)
    return gc

def getWorksheetColumnName(workSheet, sheet_name=''):
    if sheet_name == '':
        sheet_name = getSheetName()
    sheet = connect().open(sheet_name).worksheet(workSheet)
    header = sheet.row_values(1)
    return header

def updateFromCSV(csvPath, workSheet, newline='', sheet_name=''):
    if sheet_name == '':
        sheet_name = getSheetName()
    sheet = connect().open(sheet_name).worksheet(workSheet)

    #load csv
    tableList = []
    with open(csvPath, 'r', newline=newline, encoding='utf-8') as readfile:
        for row in csv.reader(readfile,delimiter=','):
            tableList.append(row)
        readfile.close()

    try:
        sheet.clear()
        print('update data to {} please don\'t exit!'.format(workSheet))
        sheet.update(tableList,value_input_option='USER_ENTERED')
    except:
        raise IOError('Update Sheet Error')

def addRow(workSheet, column, sheet_name=''):
    if sheet_name == '':
        sheet_name = getSheetName()
    sheet = connect().open(sheet_name).worksheet(workSheet)
    sheet.append_row(column,value_input_option='USER_ENTERED')

def deleteRow(workSheet, colName, value, sheet_name=''):
    if sheet_name == '':
        sheet_name = getSheetName()
    sheet = connect().open(sheet_name).worksheet(workSheet)
    dataS = sheet.get_all_records()
    rowIndex = 1
    for data in dataS:
        rowIndex += 1
        if data[colName] == value:
            sheet.delete_row(rowIndex)
            print('Sheet "{}" Deleted Row {}'.format(workSheet,rowIndex))

def getAllDataS(workSheet, sheet_name=''):
    if sheet_name == '':
        sheet_name = getSheetName()
    sheet = connect().open(sheet_name).worksheet(workSheet)
    dataS = sheet.get_all_records()
    return dataS

def setValue(workSheet,findKey=None,findValue=None,key=None,value=None, sheet_name=''):
    if sheet_name == '':
        sheet_name = getSheetName()
    dataS = getAllDataS(workSheet, sheet_name=sheet_name)
    rowIndex = 1
    for data in dataS:
        rowIndex += 1
        if not key in data:
            return None
        if data[findKey] == findValue and key in data:
            print(sheet_name)

            colIndex = 0
            for col in getWorksheetColumnName(workSheet):
                colIndex += 1
                if col == key:

                    sheet = connect().open(sheet_name).worksheet(workSheet)
                    sheet.update_cell(row=rowIndex,col=colIndex,value=value)
                    print('update cell in > row : {}  column : \'{}\'  value : {}'.format(rowIndex,key,value))
                    break
            break

def sortFisrtColumn(workSheet, sheet_name=''):
    if sheet_name == '':
        sheet_name = getSheetName()
    sheet = connect().open(sheet_name).worksheet(workSheet)
    sheet.sort((1, 'asc'))

if __name__ == '__main__':
    import pprint
    pprint.pprint(getAllDataS('AnimationTracking'))
    pass