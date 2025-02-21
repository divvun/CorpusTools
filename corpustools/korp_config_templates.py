"""
This module keeps templates of the contents of various files in the
korp-backend corpus config folder. The folder looks like this:

    config/
      attributes/
        structural/                one yaml file per structural attribute
          text_date.yaml           things that are common to a text. date,
          text_title.yaml          lang, author, title, etc...
          ...
        positional/                one yaml file per positional attribute
          lemma.yaml               properties of each word.
          pos.yaml
          ...
      corpora/
        LANG_CATEOGRY_DATE.yaml       one file per CATEGORY
        ...
      modes/                         the modes, shown in the top right on
        default.yaml                 the korp frontend webpage
        ...maybe-other.yaml
        ...

For most of our corpora, the structural and positional attributes are the same,
and therefore, we have a template of this file tree, in

    korp_config_template/

The compile_cwb_mono.py script will copy this template tree to

    <workdir>/korp_configs/LANG/

and then fill out with how much it can. All corpora/ files should be filled in,
as well as modes/default.yaml. Anything else will have to be manually adjusted,
and of course, before production, the contents should be manually inspected.
"""

from textwrap import dedent

# title and description fields of the korp corpus yaml config,
# for various known category names. If we don't know the category name,
# we insert a placeholder
CORPUS_CONFIG_TITLE_AND_DESCRIPTIONS = {
    "admin": dedent("""\
        title:
          eng: Administrative texts
          nob: Administrative tekster
          sme: Hálddahuslaš teavsttat
          fin: Hallinnolliset tekstit
        description:
          eng: Administrative texts
          nob: Administrative tekster
          sme: Hálddahuslaš teavsttat
          fin: Hallinnolliset tekstit
    """).strip(),
    "bible": dedent("""\
        title:
          eng: Religion texts
          nob: Religiøse tekster
          sme: Oskkoldatlaš teavsttat
          fin: Uskonnolliset tekstit
        description:
          eng: Texts on religion
          nob: Religiøse tekster
          sme: Teavsttat oskku birra
          fin: Uskonnolliset tekstit
    """),
    "blogs": dedent("""\
        title:
          eng: Blog texts
          nob: Bloggtekster
          sme: Bloggateavsttat
          fin: Blogitekstit
        description:
          eng: A collection of blog texts
          nob: En samling av bloggtekster
          sme: Bloggateavsttaid čoakkáldat
          fin: Blogitekstien kokoelma
    """),
    "facta": dedent("""\
        title:
          eng: Non-fiction texts
          nob: Sakprosa
          sme: Áššeprosa
          fin: Asiatekstit
        description:
          eng: A collection of non-fiction texts
          nob: Ei samling av sakprosatekster
          sme: Áššeprosateavsttaid čoakkáldat
          fin: Asiatekstien kokoelma
    """),
    "ficti": dedent("""\
        title:
          eng: Fiction texts
          nob: Skjønnlitteratur
          sme: Čáppagirjjálašvuohta
          fin: Kaunokirjallisuus
        description:
          eng: A collection of fiction texts
          nob: Ei samling av skjønnlitterære tekster
          sme: čáppagirjjálašvuođa čoakkáldat
          fin: Kaunokirjallisuuden kokoelma
    """),
    "laws": dedent("""\
        title:
          eng: Law texts
          nob: Juridiske tekster
          sme: Láhkateavsttat
          fin: Lakitekstit
        description:
          eng: A collection of legislative texts
          nob: Ei samling av lovtekster
          sme: Láhkateavsttaid čoakkaldat
          fin: Lakitekstien kokoelma
    """),
    "news": dedent("""\
        title:
          eng: News texts
          nob: Nyhetstekster
          sme: Ođasteavsttat
          fin: Uutistekstit
        description:
          eng: A collection of news texts
          nob: Ei samling av nyhetstekster
          sme: Ođasteavsttaid čoakkáldat
          fin: Uutistekstien kokoelma
    """),
    "science": dedent("""\
        title:
          eng: Science texts
          nob: Vitenskaplige tekster
          sme: Dieđalaš teavsttat
          fin: Tieteelliset tekstit
        description:
          eng: A collection of science texts such as masters theses, phd theses, and articles
          nob: Ei samling av vitenskaplige tekster, f.eks. master- og doktoravhandlinger eller artikler
          sme: Dieđalaš teavsttaid čoakkáldat, nákkosgirjjit, masterbarggut ja artihkkalat
          fin: Tieteellisten tekstien kokoelma, väitöskirjat, gradut ja tieteelliset artikkelit
    """),
    "wikipedia": dedent("""\
        title:
          eng: Wikipedia
          nob: Wikipedia
          sme: Wikipedia
          fin: Wikipedia
        description:
          eng: Wikipedia
          nob: Wikipedia
          sme: Wikipedia
          fin: Wikipedia
    """),
    "__DEFAULT__": dedent("""\
        title:
          eng: __FILLINTHISFIELD__
          nob: __FILLINTHISFIELD__
          sme: __FILLINTHISFIELD__
          fin: __FILLINTHISFIELD__
        description:
          eng: __FILLINTHISFIELD__
          nob: __FILLINTHISFIELD__
          sme: __FILLINTHISFIELD__
          fin: __FILLINTHISFIELD__
    """).strip()
}

# Template for Backend Korp corpus yaml config file
# the ones in <corpus_config>/corpora/CORPUS_ID.yaml
KORP_SETTINGS_TEMPLATE = """
id: {corpus_id}
{title_and_description}
mode:
  - name: default
pos_attributes:
  - lemma: lemma
  - pos: pos
  - msd: msd
  - ref: ref
  - word: word
  - deprel: deprel
  - dephead: dephead
struct_attributes:
  - text_title: text_title
  - text_date: text_date
  - text_id: text_id
  - text_title: text_title
  - text_lang: text_lang
  - text_orig_lang: text_orig_lang
  - text_gt_domain: text_gt_domain
  - text_first_name: text_first_name
  - text_last_name: text_last_name
  - text_nationality: text_nationality
  - text_date: text_date
  - text_datefrom: text_datefrom
  - text_dateto: text_dateto
  - text_timefrom: text_timefrom
  - text_timeto: text_timeto
  - text_sentence_count: text_sentence_count
  - text_token_count: text_token_count
context:
  - label:
      eng: 1 sentence
      nob: 1 setning
      sme: 1 cealkka
      fin: 1 lause
    value: 1 sentence
within:
  - label:
      eng: sentence
      nob: setning
      sme: cealkka
      fin: lause
    value: sentence
"""

# contents of <korp_config>/modes/default.yaml
# depends on which language it is
DEFAULT_MODE_CONTENTS = {
    "fao": dedent("""\
        order: 1
        label:
          eng: "Faroese texts"
          nob: "Færøysk tekst"
          sme: "Fearagiel teavsttat"
          fin: "Fäärin tekstit"
    """),
    "fit": dedent("""\
        order: 1
        label:
          eng: "Meänkieli texts"
          nob: "Meänkieli-tekst"
          sme: "Meänkieliteavsttat"
          fin: "Meänkielen tekstit"
    """),
    "fkv": dedent("""\
        order: 1
        label:
          eng: "Kven text"
          nob: "Kvensk tekst"
          sme: "Kveanateavsttat"
          fin: "Kveenin tekstit"
    """),
    "koi": dedent("""\
        order: 1
        label:
          eng: Komi-Permyak texts
          nob: Komipermjakiske tekster
          sme: Komipermjaka teavsttat
          fin: Komipermjakin tekstit
          rus: Коми-пермяцские тексты
    """),
    "kpv": dedent("""\
        order: 1
        label:
          eng: Komi-Zyrian texts
          nob: Komisyrjenske tekster
          sme: Komigiela teavsttat
          fin: Komisyrjäänin tekstit
          rus: коми-зырянские тексты
    """),
    "mdf": dedent("""\
        order: 1
        label:
          eng: Moksha texts
          nob: Moksjatekster
          sme: Mokšagiela teavsttat
          fin: Mokšan tekstit
          rus: Тексты мокшаского языка
    """),
    "mhr": dedent("""\
        order: 1
        label:
          eng: Meadow Mari texts
          nob: Østmariske tekster
          sme: Niitomarigiela teavsttat
          fin: Niitymarin tekstit
    """),
    "mrj": dedent("""\
        order: 1
        label:
          eng: Hill Mari texts
          nob: Vestmariske tekster
          sme: Várremarigiela teavsttat
          fin: Vuorimarin tekstit
          rus: Горномарийские тексты
    """),
    "myv": dedent("""\
        order: 1
        label:
          eng: Erzya texts
          nob: Erzjatekster
          sme: Ersagiela teavsttat
          fin: Ersän tekstit
          rus: Эрщянские тексты
    """),
    "olo": dedent("""\
        order: 1
        label:
          eng: "Livvi texts"
          nob: "Livvisk tekst"
          sme: "Livvigiel teavsttat"
          fin: "Livvin tekstit"
    """),
    "sma": dedent("""\
        order: 1
        label:
          nob: "Sørsamiske tekster"
          eng: "South sami texts"
          sme: "Lullisámi teavsttat"
          fin: "Eteläsaamen tekstit"
        primaryColor: '#EDFCD5'
        primaryLight: '#f7fceb'
        wordpicture: false
    """),
    "sme": dedent("""\
        order: 1
        label:
          nob: "Nordsamiske tekster"
          eng: "North sami texts"
          sme: "Davvisámi teavsttat"
          fin: "Pohjoissaamen tekstit"
    """),
    "smj": dedent("""\
        order: 1
        label:
          nob: "Lulesamiske tekster"
          eng: "Lule sami texts"
          sme: "Julevsámi teavsttat"
          fin: "Luulajansaamen tekstit"
        primaryColor: '#E0F4F4'
        primaryLight: '#F2FFFF'
        wordpicture: false
    """),
    "smn": dedent("""\
        order: 1
        label:
          nob: "Enaresamiske tekster"
          eng: "Enaresami texts"
          sme: "Anársámi teavsttat"
          fin: "Inarinsaamen tekstit"
        primaryColor: '#EDFCD5'
        primaryLight: '#f7fceb'
        wordpicture: false
    """),
    "sms": dedent("""\
        order: 1
        label:
          nob: "Skoltsamiske tekster"
          eng: "Skolt Saami texts"
          sme: "Nuortalaš teavsttat"
          fin: "Koltansaamen tekstit"
        primaryColor: '#EDFCD5'
        primaryLight: '#f7fceb'
        wordpicture: false
    """),
    "udm": dedent("""\
        order: 1
        label:
          eng: Udmurt texts
          nob: Udmurtiske tekster
          sme: Udmurtagiela teavsttat
          fin: Udmurtin tekstit
          rus: Удмуртские тексты
    """),
    "vep": dedent("""\
        order: 1
        label:
          eng: "Veps texts"
          nob: "Vepsisk tekst"
          sme: "Vepsateavsttat"
          fin: "Vepsän tekstit"
    """),
    "vro": dedent("""\
        order: 1
        label:
          eng: "Võro texts"
          nob: "Võro-tekst"
          sme: "Võroteavsttat"
          fin: "Võron tekstit"
    """),
    "__DEFAULT__": dedent("""\
        order: 1
        label:
          eng: __FILLINTHISFIELD__
          nob: __FILLINTHISFIELD__
          sme: __FILLINTHISFIELD__
          fin: __FILLINTHISFIELD__
    """)
}
