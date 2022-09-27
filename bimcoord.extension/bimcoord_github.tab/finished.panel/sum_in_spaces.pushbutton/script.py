# -*- coding: utf-8 -*-
#region Вводная часть
from Autodesk.Revit import DB
from rpw import db, ui
from System import Guid
from pyrevit import script

__title__ = "Количество светильников"
__author__ = "@butyric_acid" #TELEGRAM
__doc__ = '''   Данный скрипт рассчитывает количество светильников, находящихся в пространстве и записывает значение в параметр.

    Прим.: Программа не выполнится при наличии пространств, находящихся в разных стадиях.
    
    Прим.: Программа не выполнится, если заполняемый параметр не изменяется по экземплярам группы и в проекте существуют несколько экземпляров групп.'''

PARAMETER_FOR_WRITING = Guid("0a747176-e3e2-4c08-8cd9-17b04125e7c9") # Параметр для записи
doc = __revit__.ActiveUIDocument.Document
output = script.get_output()
#endregion

#region Функции
def revit_collector(ost):
    '''Реализация коллектора элементов Revit
    через функцию для упрощения кода

    '''
    elements = DB.FilteredElementCollector(doc).\
        OfCategory(ost).\
        WhereElementIsNotElementType().\
        ToElements()
    return elements

def task_dialog_form(head, body, stopprogram = False):
    '''Конструктор формы диалога для Revit
    Также для упрощения кода

    '''
    ui.forms.TaskDialog(head,
    content=body,
    title = "Программа: "+__title__,
    buttons = ['OK'],
    show_close = False).show()
    if stopprogram: script.exit() 
#endregion

#region Условия невыполнения программы:
spaces = revit_collector(DB.BuiltInCategory.OST_MEPSpaces)
lighting_fixtures = revit_collector(DB.BuiltInCategory.OST_LightingFixtures)
total_lighting_fixtures = str(len(lighting_fixtures))
phases = [doc.GetElement(i) for i in (set(i.Parameter[DB.BuiltInParameter.ROOM_PHASE].AsElementId() for i in spaces))]
if len(spaces) == 0:
    task_dialog_form('Пространства отсутствуют в проекте',
    '''В данном проекте отсутсвуют пространства
Выполните расстановку пространств''', True)
elif len(phases) != 1:
    task_dialog_form('Пространства существуют более чем в одной стадии',
    '''Пространства должны находится в одной стадии
Удалите лишние пространства через спецификацию''', True)
elif len(lighting_fixtures) == 0:
    task_dialog_form('В проекте отсутствуют осветительные приборы',
    '''В данном проекте отсутсвуют осветительные приборы''', True)
#endregion

#region Создать словарь элементов {str(id_пространства+имя+тип): [[id_элементов,], количество]}:
DICT_ = {} # Переменная создаваемого словаря
report_space = [] # Список, собирающий светильники, которые находятся вне пространства
for i in lighting_fixtures:
    try:
        j = i.Space[phases[0]].Id.ToString()+ " " +\
            i.Parameter[DB.BuiltInParameter.ELEM_FAMILY_PARAM].AsValueString()+ " " +\
            i.Parameter[DB.BuiltInParameter.ELEM_TYPE_PARAM].AsValueString()
        if not j in DICT_.keys():
            DICT_[j] = [[i.Id,], 1]
        else:
            DICT_[j][0].append(i.Id)
            DICT_[j][1] += 1
    except:
        report_space.append(output.linkify(i.Id))
#endregion

#region Запись параметров:
def write_sum_lights(i):
    '''Функция для ускорения отработки цикла'''

    report_param = []
    for j in i[0]: # j - id элемента
        try:
            doc.GetElement(j).get_Parameter(PARAMETER_FOR_WRITING).Set(i[1]) # i[1] - Количество светильников в пр-ве
        except:
            report_param.append(output.linkify(j))
    return report_param

with db.Transaction("Плагин: "+__title__):
    for i in DICT_.values():
        report_param = write_sum_lights(i)
#endregion

#region Вывод сообщений: 
if len(report_param) != 0 or len(report_space) != 0:
    print("Параметры заполнены, но программа завершила работу с ошибками:")
    if len(report_param) != 0:
        print("У следующих элементов не добавлен параметр, либо добавлен как параметр типа: ")
        for i in report_param:
            output.print_md(i)
    if len(report_space) != 0:
        print("Следующие элементы находятся вне пространства: ")
        for i in report_space:
            output.print_md(i)
else:
    task_dialog_form('Параметр для светильников успешно заполнен',"")
print("Работа плагина " + __title__ + " завершена")
#endregion