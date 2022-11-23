import table_5_2
import pdf_2_1_3


def main():
    type_out = input('Введите вид формирования данных: ')
    if type_out == 'Вакансии':
        table_5_2.get_table()
    elif type_out == 'Статистика':
        pdf_2_1_3.get_pdf()
    else:
        print('Неверный ввод!')


if __name__ == '__main__':
    main()
