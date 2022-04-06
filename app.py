import numpy as np
import pandas as pd
import streamlit as st

st.set_option('deprecation.showPyplotGlobalUse', False)

img_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn' \
          ':ANd9GcS2j3GxJqj8vYW9Tei7I51uYgiWkQa90LSWTQ&usqp=CAU '
st.set_page_config(
    layout="wide", initial_sidebar_state="auto",
    page_title="Gross to Net", page_icon=img_url)

efka_options = {
    'Ειδική': 1632,
    '1η': 2640,
    '2η': 3144,
    '3η': 3744,
    '4η': 4476,
    '5η': 5340,
    '6η': 6912,
}

st.title('ΜΕΙΚΤΑ ΣΕ ΚΑΘΑΡΑ')
st.subheader('υπολογισμός κρατήσεων επιχείρησης παροχής υπηρεσιών')


def convert(number):
    currency_string = "€ {:,.2f}".format(number)
    return currency_string


def calculate_income():
    st.markdown('### Έσοδα (τζίρος)')
    me_fpa = st.number_input('Ετήσιες αποδοχές που έχουν ΦΠΑ', min_value=0)
    xwris_fpa = st.number_input('Ετήσιες αποδοχές που δεν έχουν ΦΠΑ',
                                min_value=0)

    without_fpa = me_fpa / 1.24

    total_income = without_fpa + xwris_fpa

    return total_income


def calculate_expenses():
    st.markdown('### ΕΞΟΔΑ')
    logistika = st.number_input('Ετήσια λογιστικά έξοδα', min_value=0)
    enoikia = st.number_input('Ενοίκια', min_value=0)
    revma = st.number_input('Ρεύμα', min_value=0)
    nero = st.number_input('Νερό', min_value=0)
    internet = st.number_input('Τηλέφωνα-Internet', min_value=0)
    other_expenses = st.number_input('Aναλώσιμα/Λοιπά έξοδα', min_value=0)

    total = logistika
    total += enoikia
    total += revma
    total += nero
    total += internet
    total += other_expenses

    efka_help = 'Από 01/01/2020 δημιουργούνται επτά (7) ασφαλιστικές ' \
                'κατηγορίες για ελεύθερους επαγγελματίες και ' \
                'αυτοαπασχολούμενους, εκ των οποίων μία θεωρείται ειδική ' \
                'ασφαλιστική κατηγορία και απευθύνεται σε νέους ' \
                'επαγγελματίες (πρώτα πέντε έτη ασφάλισης). '

    st.markdown('### ΕΦΚΑ')
    efka = st.selectbox('Ασφ. Κατηγορία', options=efka_options,
                        help=efka_help, )
    st.markdown(f'Ποσό: **{convert(efka_options[efka])}**')

    total += efka_options[efka]
    return total


def compute_tax_on_atomic(amount_to_be_taxed):
    st.markdown('### Ανάλυση Φορολογίας Ατομικής Επιχείρησης')

    x = amount_to_be_taxed
    tax_prc_values = [0.09, 0.22, 0.28, 0.36, 0.44]
    step = 10_000
    tax_values = []
    for f in tax_prc_values[:-1]:
        if x > 0:
            x -= step
            tax_values.append(f * step)
        else:
            break

    if x > 0:
        tax_values.append(tax_prc_values[-1] * x)

    total_tax = sum(tax_values)

    sintelestes = ["{:.0%}".format(i) for i in tax_prc_values]
    sintelestes.append('Σύνολο')
    tax_values.append(total_tax)
    tax_values = [convert(i) for i in tax_values]

    tax_df = pd.DataFrame({'Συντελεστής': sintelestes,
                           'Ποσό': tax_values})

    st.dataframe(tax_df)

    st.markdown(f'**Συνολικός Κύριος Φόρος Ατομικής '
                f'Επιχείρησης: {round(total_tax, 3)}**')

    net_value = amount_to_be_taxed - total_tax
    return total_tax, net_value


def compute_tax_for_oe_and_ee(amount_to_be_taxed):
    st.markdown('### Ανάλυση Φορολογίας ΟΕ-ΕΕ Επιχείρησης')
    tax_prc = 0.22

    total_tax = tax_prc * amount_to_be_taxed
    extra_tax = 1000  # telos epitideuvatos

    total_tax += extra_tax
    column1 = [
        'Συντελεστής 22%',
        'Τέλος Επιτηδεύματος',
        'Σύνολο'
    ]
    column2 = [
        convert(tax_prc * amount_to_be_taxed),
        convert(extra_tax),
        convert(total_tax)
    ]
    data = pd.DataFrame({'Ανάλυση': column1, 'Ποσό': column2})
    st.dataframe(data)

    st.markdown(f'**Συνολικός Κύριος Φόρος OE-EE '
                f'Επιχείρησης: {round(total_tax, 3)}**')

    net_value = amount_to_be_taxed - total_tax
    return total_tax, net_value


def analyse_per_month(value):
    twelve = round(value / 12, 2)
    fourteen = round(value / 14, 2)

    labels = [
        'Συνολικό καθαρό εισόδημα',
        'Καθαρό εισόδημα ανά μήνα για 12 μήνες',
        'Καθαρό εισόδημα ανά μήνα για 14 μήνες',
    ]
    values = [
        convert(value),
        convert(twelve),
        convert(fourteen)
    ]

    data = pd.DataFrame({'Καθαρά Κέρδη': labels,
                         'Ποσό': values})

    st.dataframe(data)


col1, col2 = st.columns(2)
with col1:
    total_in = calculate_income()
with col2:
    expenses = calculate_expenses()

run = st.button('Υπολογισμός Κρατήσεων')
if run and total_in > 0:
    to_be_taxed = total_in - expenses
    labels = ['Συνολικά έσοδα (χωρίς ΦΠΑ)',
              'Συνολικά έξοδα & ΕΦΚΑ',
              'Ποσό προς φορολόγηση (καθαρά κέρδη)']

    numbers = [convert(total_in),
               convert(expenses),
               convert(to_be_taxed)]

    df = pd.DataFrame({'Αποτελέσματα': labels, 'Ποσό': numbers})

    st.dataframe(df)

    col1, col2 = st.columns(2)

    st.markdown('### Η προκαταβολή φόρου δεν λαμβάνεται υπόψιν στους '
                'υπολογισμούς')

    with col1:
        atomic_tax, atomic_net = compute_tax_on_atomic(to_be_taxed)
        analyse_per_month(atomic_net)
    with col2:
        ee_tax, ee_net = compute_tax_for_oe_and_ee(to_be_taxed)
        analyse_per_month(ee_net)
