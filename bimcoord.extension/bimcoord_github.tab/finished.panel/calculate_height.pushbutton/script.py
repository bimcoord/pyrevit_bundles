# -*- coding: utf-8 -*-
from Autodesk.Revit import DB
from System import Guid
from rpw.ui.forms import SelectFromList
from pyrevit import script

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
output = script.get_output()

HEIGHT_PARAMETER = Guid("79031cd4-3c6e-4aeb-89c3-5aaca698eae4") #Укажите GUID параметра для заполнения
THRESHOLD = 100 # 100 мм
FOOT_PER_MILLIMETER = 304.8

__title__ = '''Высота элемента'''
__author__ = "@butyric_acid" #TELEGRAM
__doc__ = '''   Данный скрипт вычисляет расстояние от точки элемента до ближайшего перекрытия и сверяет полученное значение со значением параметра.
Если разница между этими значениями превышает 100 мм в определенном элементе, то выводится ID этого элемента.
Если параметр не заполнен или равен 0, то значение перезапишеться на фактическое. Скрипт запускается с любого вида.

    SHIFT: При запуске программы с зажатой клавишей shift в параметр записывается актуальное значение высоты от отметки чистого пола.
    
    Прим.: Обязательно включите рабочие наборы со связями архетектуры.
    Прим.: Параметр заполняется только для промаркированных элементов.
    Прим.: Точка, от которой рассчитывается высота кабельного лотка, трубы и других протяженных элементов - середина минус половина высоты.'''
#region Функции
def get_point_from_cabletray(element):
    '''Функция поиска положения точки для элементов типа "Кабельный лоток"'''

    _h = element.Parameter[DB.BuiltInParameter.RBS_CABLETRAY_HEIGHT_PARAM].AsDouble()
    _temp = (i for i in element.Location.Curve.Tessellate())
    xyz1 = next(_temp)
    xyz2 = next(_temp)
    xyz = DB.XYZ(
        (xyz1.X + xyz2.X)/2,
        (xyz1.Y + xyz2.Y)/2,
        ((xyz1.Z + xyz2.Z)/2) - (_h/2)
    )
    return xyz

def get_point_from_pipe(element):
    '''Функция поиска положения точки для элементов типа "Труба"'''

    _temp = (i for i in element.Location.Curve.Tessellate())
    xyz1 = next(_temp)
    xyz2 = next(_temp)
    xyz = DB.XYZ(
        (xyz1.X + xyz2.X)/2,
        (xyz1.Y + xyz2.Y)/2,
        ((xyz1.Z + xyz2.Z)/2)
    )
    return xyz
#endregion

_categories_for_combobox = {
    'Осветительные приборы': {
        'Категория марки': DB.BuiltInCategory.OST_LightingFixtureTags,
        'Функция поиска точек': lambda x: x.Location.Point
    },
    'Кабельные лотки': {
        'Категория марки': DB.BuiltInCategory.OST_CableTrayTags,
        'Функция поиска точек': get_point_from_cabletray
    },
    'Трубы': {
        'Категория марки': DB.BuiltInCategory.OST_PipeTags,
        'Функция поиска точек': get_point_from_pipe
    }
    }

selected_category = SelectFromList(
    'Программа: "{}"'.format(__title__),
    _categories_for_combobox
)

transaction = DB.Transaction(doc, 'Плагин: "{}"'.format(__title__))
transaction.Start()

# Создание 3D-вида
_view_family_types = DB.FilteredElementCollector(doc).\
    OfClass(DB.ViewFamilyType).\
    ToElements()
_view_family_type_3D = [i for i in _view_family_types if i.ViewFamily == DB.ViewFamily.ThreeDimensional][0]
view3D__1 = DB.View3D.CreateIsometric(
    doc,
    _view_family_type_3D.Id
)
# Создание класса поиска элементов
reference_intersector = DB.ReferenceIntersector(
    DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Floors),
    DB.FindReferenceTarget.Face,
    view3D__1
    )
reference_intersector.FindReferencesInRevitLinks = True

# Проверка на то, добавлен ли параметр как параметр проекта
_tags_collector = DB.FilteredElementCollector(doc).\
    OfCategory(selected_category['Категория марки']).\
    WhereElementIsNotElementType().\
    ToElements()
tagged_elements = [tag.GetTaggedLocalElement() for tag in _tags_collector]
_ = [tagged_element.get_Parameter(HEIGHT_PARAMETER) == None for tagged_element in tagged_elements]
if len(_) == 0 or any(_):
    print("Не для всех элементов категории добавлен параметр, либо ни один из элементов выбранной категории не промаркирован") 
    print("Работа плагина " + __title__ + " завершена")
    transaction.RollBack()
    script.exit()

report_no_height = [] # Список элементов, которые находятся вне пола
report_height = [] # Список элементов с большой разницей в высоте между фактическим значением и параметром
for tagged_element in tagged_elements:
    _tagged_element_ref_with_context = reference_intersector.FindNearest( # Высота светильников  в футах
        selected_category['Функция поиска точек'](tagged_element),
        DB.XYZ(0,0,-1)
        )
    if _tagged_element_ref_with_context is None:
        report_no_height.append(tagged_element.Id)
    else:
        tagged_element_height_real = _tagged_element_ref_with_context.Proximity * FOOT_PER_MILLIMETER
        _parameter_height = tagged_element.get_Parameter(HEIGHT_PARAMETER)

        if __shiftclick__:
            _parameter_height.Set(tagged_element_height_real)
        else:
            if _parameter_height.AsDouble() == 0:
                _parameter_height.Set(tagged_element_height_real)
        
        _difference_between = abs(tagged_element_height_real - _parameter_height.AsDouble())
        if _difference_between > THRESHOLD:
            report_height.append([tagged_element.Id, _difference_between])

doc.Delete(view3D__1.Id) #Удаление 3D - вида, чтобы не плодить их лишний раз

#Вывод сообщений об ошибках
no_errors = True
if len(report_height) != 0:
    no_errors = False
    print("Следующие элементы имеют высокую разницу между фактической высотой и параметром.")
    for report in report_height:
        output.print_md("У элемента {0} разница в расстоянии {1}".format(output.linkify(report[0]), report[1]))
if len(report_no_height) != 0:
    no_errors = False
    print("Под следующими элементами нет пола")
    for report in report_no_height:
        output.print_md(output.linkify(report))
if no_errors:
    print("Скрипт " + __title__ + " завершился без ошибок")

print("Работа плагина " + __title__ + " завершена")
transaction.Commit()


