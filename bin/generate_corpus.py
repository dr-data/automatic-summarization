#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Main script to run training and evaluation of models."""

import os
import re
import errno
import random

import tensorflow as tf

tf.flags.DEFINE_string("wex_articles", "",
                       """Path to the articles.tsv file from 'Wikipedia
                       Extraction (WEX)', a processed dump of the English
                       language Wikipedia available as part of Amazon's
                       AWS Public Datasets inititive.""")
tf.flags.DEFINE_string("output_dir", "",
                       """The directory to write the resulting corpus to""")

FLAGS = tf.flags.FLAGS

class WEXCorpusGenerator:
  """Class which generates the WEX corpus from the WEX dump.

  Params:
    output_dir: The directory to which the WEX corpus is written.
    wex_articles: The path to the articles.tsv file from WEX dump.
  """
  def __init__(self, output_dir, wex_articles):
    # Validate wex_articles exists 
    if not os.path.isfile(wex_articles):
      raise ValueError("wex_articles must specify a valid file")

    # Create output_dir if it doesn't exist
    try:
        os.makedirs(output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    # Set member variables
    self._output_dir = output_dir 
    self._wex_articles = wex_articles

  def run(self):
    # Set seed for reproducability
    random.seed(42)

    # Create paths to train, validation, and test corpora
    test_corpus_path = os.path.join(self._output_dir, "test_corpus.tsv")
    train_corpus_path = os.path.join(self._output_dir, "train_corpus.tsv")
    validation_corpus_path = os.path.join(self._output_dir, "validation_corpus.tsv")

    # Open all corpora files
    with open(test_corpus_path, "a") as test_corpus:
      with open(train_corpus_path, "a") as train_corpus:
        with open(validation_corpus_path, "a") as validation_corpus:
          # Open articles.tsv file
          with open(self._wex_articles) as wex_articles:
            # Loop over lines in wex_articles
            for line in wex_articles:
              summary, text = self._parse_line(line)
              if None == summary or None == text:
                continue
              random_number = random.random() 
              if random_number < 0.60:
                train_corpus.write(summary + '\t' + text + '\n')
              elif random_number < 0.80:
                validation_corpus.write(summary + '\t' + text + '\n')
              else:
                test_corpus.write(summary + '\t' + text + '\n')

  def _parse_line(self, line):
    # Parse the tab seperated values
    elements = line.split("\t")
    # Obtain the article title according to WEX's format
    raw_title = elements[1]
    # Ignore disambiguation pages 
    if raw_title.endswith('(disambiguation)'):
      return (None, None)
    if raw_title == 'Ambient':
      return (None, None)
    # Ignore articles for a given day of the month or month of the year
    matchObj = re.match(r'^January|February|March|April|May|June|July|August|September|October|November|December \d\d?\d?\d?$', raw_title)
    if matchObj: 
      return (None, None)
    # Ignore articles that are simply a list of other articles 
    matchObj = re.match(r'^List of [^ ]+ topics', raw_title)
    if matchObj: 
      return (None, None)
    # Obtain the final element, raw text according to WEX's format
    raw_text = elements[4]
    # Normalize raw_text
    raw_text = self._normalize_raw_text(raw_text)
    # Obtain the location of the end of the summary
    summary_end = raw_text.find('\\n\\n')
    # If line is malformed return
    if -1 == summary_end:
      return (None, None)
    # Obtain summary
    summary = raw_text[0:summary_end]
    # Obtain text
    text = raw_text[summary_end + 4:]
    # Strip summary and text of whitespace
    text = text.strip()
    summary = summary.strip()
    # Ignore malformed texts
    if (not text) or (not summary):
      return (None, None)
    # If line is malformed return
    if len(text) < len(summary):
      return (None, None)
    # Ignore disambiguation pages
    if summary.endswith('may refer to:'):
      return (None, None)
    # Ignore pages listing abbreviation definitions 
    if summary.endswith('may mean:'):
      return (None, None)
    # Ignore malformed article 'Affirming the consequent'
    if summary.startswith('Affirming the consequent, sometimes called converse error'):
      return (None, None)
    # Ignore malformed article 'Transport in Angola'
    if summary.startswith('Transport in Angola comprises:'):
      return (None, None)
    # Ignore obsolete articles
    if summary.startswith('The following list is obsolete'):
      return (None, None)
    # Ignore malformed articles
    if summary.startswith('in the Roman Catholic Church'):
      return (None, None)
    if summary == '300px':
      return (None, None)
    matchObj = re.match(r'^\d+px', summary)
    if matchObj: 
      return (None, None)
    # Ignore trailing ' For example' 
    if summary.endswith(' For example:'):
      summary = summary[:-13]
    # Ignore trailing ' Consider for instance the equation' 
    if summary.endswith(' Consider for instance the equation'):
      summary = summary[:-35]
    # Fix malformed summaries
    if summary.startswith('('):
      summary = raw_title + ' ' + summary 
    # Fix some randomness
    summary = summary.replace(' ( (UK), (US))', '')
    # Ignore articles that simply list definitions' 
    if summary.endswith('has several meanings:'):
      return (None, None)
    # Ignore articles that simply list places' 
    if summary.endswith('may refer to the following places:'):
      return (None, None)
    # Return results
    return (summary, text)

  def _normalize_raw_text(self, raw_text):
    raw_text = raw_text.strip()
    if raw_text.startswith("''"):
      raw_text = raw_text[2:]
    if raw_text.startswith('\\n\\n'):
      raw_text = raw_text[4:]
    if raw_text.startswith('rightrightAn'):
      raw_text = raw_text[10:]
    if raw_text.startswith('rightAlkanes'):
      raw_text = raw_text[5:]
    if raw_text.startswith('thumb\\n\\n'):
      raw_text = raw_text[9:]
    if raw_text.startswith('right\\n\\n'):
      raw_text = raw_text[9:]
    if raw_text.startswith('thumb'):
      raw_text = raw_text[5:]
    if raw_text.startswith('thumb\\n\\n'):
      raw_text = raw_text[9:]
    if raw_text.startswith('frame'):
      raw_text = raw_text[5:]
    if raw_text.startswith('thumbAdobe'):
      raw_text = raw_text[5:]
    if raw_text.startswith('rightAn'):
      raw_text = raw_text[5:]
    if raw_text.startswith('thumbthumbthumbThe'):
      raw_text = raw_text[15:]
    if raw_text.startswith(' \\n\\n'):
      raw_text = raw_text[5:]
    raw_text = raw_text.replace(' (,  – March 6, 1982),', '')
    raw_text = raw_text.replace(' (, al-Jazā’ir, Berber: Dzayer, )', '')
    raw_text = raw_text.replace('thumb\\n\\n', '\\n\\n')
    raw_text = raw_text.replace('()', '')
    raw_text = raw_text.replace('  ,', ',')
    raw_text = raw_text.replace(' ,', ',')
    raw_text = raw_text.replace('; )', ')')
    raw_text = raw_text.replace('\\t', ' ')
    raw_text = raw_text.replace('(, from Greek', '(from Greek')
    raw_text = raw_text.replace(' (,  Alyaska)', '')
    raw_text = raw_text.replace('  ', ' ')
    raw_text = raw_text.replace(')was', ') was')
    raw_text = raw_text.replace(' (, pronounced )', '')
    raw_text = raw_text.replace('(German: ; English: ) ', '')
    raw_text = raw_text.replace(' (, )', '')
    raw_text = raw_text.replace(' (,, )', '')
    raw_text = raw_text.replace("Arabic word for God.'", "Arabic word for 'God.'")
    raw_text = raw_text.replace(' (Pronounced )', '')
    raw_text = raw_text.replace('is a Japanese martial art developed by Morihei Ueshiba', 'Aikido is a Japanese martial art developed by Morihei Ueshiba')
    raw_text = raw_text.replace('Aquarius ( is a constellation', 'Aquarius is a constellation')
    raw_text = raw_text.replace('is animation in Japan and considered to be', 'Anime is animation in Japan and considered to be')
    if raw_text.startswith('right'):
      raw_text = raw_text[5:]
    raw_text = raw_text.replace(' or, Mégas Aléxandros; ', '')
    raw_text = raw_text.replace(' ( (informally: ))', '')
    raw_text = raw_text.replace(' (, Aigaio Pelagos, );, Adalar Denizi)', '')
    raw_text = raw_text.replace(' (pronounced )', '')
    raw_text = raw_text.replace('(Stockholm, 21 October 1833 - Sanremo, Italy, 10 December 1896) was a Swedish chemist', 'Alfred Nobel (Stockholm, 21 October 1833 - Sanremo, Italy, 10 December 1896) was a Swedish chemist')
    raw_text = raw_text.replace('was a prominent Japanese filmmaker, film producer, and screenwriter. His first credited film', 'Akira Kurosawa was a prominent Japanese filmmaker, film producer, and screenwriter. His first credited film')
    if raw_text.startswith('250pxAn'):
      raw_text = raw_text[5:]
    raw_text = raw_text.replace('(, ', '(')
    raw_text = raw_text.replace('(Russian:, Anna Sergeevna Kurnikova', '(Russian: Anna Sergeevna Kurnikova')
    raw_text = raw_text.replace('(; after Gnosticism)', '(after Gnosticism)')
    raw_text = raw_text.replace(' ( or [in compounds or as adjective])', '')
    raw_text = raw_text.replace("(; ass'-ta-tyne)", "(ass'-ta-tyne)")
    raw_text = raw_text.replace('Aleph 20px', 'Aleph')
    raw_text = raw_text.replace('(born Berthold Konrad Hermann Albert Speer and ; March 19, 1905 – September 1, 1981)', '(born Berthold Konrad Hermann Albert Speer; March 19, 1905 – September 1, 1981)')
    raw_text = raw_text.replace(' (; ; ; ; )', '')
    raw_text = raw_text.replace(' ( in French)', '')
    if raw_text.startswith('thumbthumbthumbthumb250px250pxthumbAchill'):
      raw_text = raw_text[35:]
    raw_text = raw_text.replace(' ()', '')
    raw_text = raw_text.replace('Its area is . ', '')
    if raw_text.startswith('200pxAalborg'):
      raw_text = raw_text[5:]
    raw_text = raw_text.strip()
    if raw_text.startswith('thumb'):
      raw_text = raw_text[5:]
    raw_text = raw_text.replace(' (: )', '')
    if raw_text.startswith(', known as Abu Ali Sina Balkhi'):
      raw_text = 'Avicenna' + raw_text
    raw_text = raw_text.replace(' (Ancient Greek: )', '')
    raw_text = raw_text.replace('(; Latin: Venus)', '(Latin: Venus)')
    raw_text = raw_text.replace(' (; Ancient Greek:, Modern Greek: )', '')
    raw_text = raw_text.replace('application -let', 'application-let')
    if raw_text.startswith('nail\\n\\n'):
      raw_text = raw_text[8:]
    raw_text = raw_text.replace('Alan Mathison Turing,,  ', 'Alan Mathison Turing ')
    raw_text = raw_text.replace(' (;, Athina, )', '')
    raw_text = raw_text.replace(' ( )', '')
    raw_text = raw_text.replace('south of the Indonesia island of Roti at .', 'south of the Indonesia island of Rote.')
    raw_text = raw_text.replace(' IAST:,, ', '')
    raw_text = raw_text.replace('Pan-America$2', 'Pan-American')
    if raw_text.startswith('right\\n\\n'):
      raw_text = raw_text[9:]
    if raw_text.startswith('to most kinds of particles, there'):
      raw_text = 'T' + raw_text[1:]
    raw_text = raw_text.replace('(; meaning "Alberta lizard")', '(meaning "Alberta lizard")')
    raw_text = raw_text.replace('(; modern Αμβρακία)', '(Greek Αμβρακία)')
    raw_text = raw_text.replace('plain.rightIt', 'plain. It')
    matchObj = re.match(r'^(\[\[File:.+\]\])(.+)', raw_text)
    if matchObj: 
      raw_text = matchObj.group(2)
    matchObj = re.match(r"^('\[\[File:.+\]\])(.+)", raw_text)
    if matchObj: 
      raw_text = matchObj.group(2)
    matchObj = re.match(r'^(\[\[File:.+\|)(.+)', raw_text)
    if matchObj: 
      raw_text = matchObj.group(2)
    raw_text = raw_text.replace('phobia..', 'phobia.')
    raw_text = raw_text.replace('successor of Omri .', 'successor of Omri.')
    raw_text = raw_text.replace(" (  Avrohom or Avruhom ;, ; Ge'ez:, )", "")
    raw_text = raw_text.replace('(; March 28 1522 – January 8 1557)', '(March 28 1522 – January 8 1557)')
    raw_text = raw_text.replace('(; c. 1100–18 November 1170)', '(c. 1100–18 November 1170)')
    index = raw_text.find('(disambiguation).')
    if -1 != index:
      raw_text = self._normalize_raw_text(raw_text[index + 17:])
    raw_text = raw_text.replace(':tr:', '')
    if raw_text.startswith('(also called Ezo in historical texts)'):
      raw_text = 'Aachen ' + raw_text
    raw_text = raw_text.replace(' / (ancient Greek: )', '')
    raw_text = raw_text.replace(' (; or, less commonly but more correctly', ', or, less commonly but more correctly')
    raw_text = raw_text.replace('(; ; 1804 in Kahak, Iran – 1881 in Bombay, India)', '(1804 in Kahak, Iran – 1881 in Bombay, India)')
    raw_text = raw_text.replace(' (Classical Latin: )', '')
    raw_text = raw_text.replace(', Classical Latin: ', '')
    raw_text = raw_text.replace(' (Greek: )', '')
    raw_text = raw_text.replace(' (Greek )', '')
    raw_text = raw_text.replace('(; ; 5 August 1461 – 19 August 1506)', '(5 August 1461 – 19 August 1506)')
    raw_text = raw_text.replace(' (Gr. )', '')
    raw_text = raw_text.replace('(Ancient Greek:, c. 375 BC – c. 275 BC)', '(c. 375 BC – c. 275 BC)')
    raw_text = raw_text.replace('Alexei Petrovich Romanov ( – ),', 'Alexei Petrovich Romanov,')
    raw_text = raw_text.replace(' (pronounced ;, )', '')
    if raw_text.startswith('nailAn'):
      raw_text = raw_text[4:]
    raw_text = raw_text.replace('resources needed to specify the object. For example, consider the following', 'resources needed to specify the object.\\n\\nFor example, consider the following')
    raw_text = raw_text.replace('(; c. 849 – October 26, c. 899)', '(c. 849 – October 26, c. 899)')
    raw_text = raw_text.replace('(; 8 February 1291 – 28 May 1357)', '(8 February 1291 – 28 May 1357)')
    raw_text = raw_text.replace(' (in Greek, )', '')
    raw_text = raw_text.replace('Ambrosius Aurelianus, ;', 'Ambrosius Aurelianus, ')
    raw_text = raw_text.replace('( – Amphípolis)', '(Amphípolis)')
    raw_text = raw_text.replace('population of 3 623', 'population of 3623')
    raw_text = raw_text.replace('( ănʹə-zärk; fl. 340 BC)', '(ănʹə-zärk; fl. 340 BC)')
    raw_text = raw_text.replace('(; ; March 25, 1297, Constantinople', '(March 25, 1297, Constantinople')
    raw_text = raw_text.replace('[[Apollo Command/Service Module|Command/Service Module]]', 'Apollo Command/Service Module ')
    raw_text = raw_text.replace('(German ; born July 30, 1947)', '(born July 30, 1947)')
    raw_text = raw_text.replace('&amp;', '&')
    raw_text = raw_text.replace('(; 1103 – 1148)', '(1103 – 1148)')
    raw_text = raw_text.replace(' ( (UK), (US))', '')
    raw_text = raw_text.replace(' ( long, 3-19 km or 2-12 miles wide', '')
    raw_text = raw_text.replace('Bahmanshir outlet of the Karun River)', 'Bahmanshir outlet of the Karun River')
    raw_text = raw_text.replace(' (properly, but commonly or )', '')
    raw_text = raw_text.replace(' (cf. )', '')
    if raw_text.startswith('rightthumbthumb\\n\\n'):
      raw_text = raw_text[19:]
    raw_text = raw_text.replace('&amp;', '&')
    raw_text = raw_text.replace('&lt;', '<')
    raw_text = raw_text.replace('&gt;', '>')
    raw_text = raw_text.replace('&Agrave;', 'À')
    raw_text = raw_text.replace('&Aacute;', 'Á')
    raw_text = raw_text.replace('&Acirc;', 'Â')
    raw_text = raw_text.replace('&Atilde;', 'Ã')
    raw_text = raw_text.replace('&Auml;', 'Ä')
    raw_text = raw_text.replace('&Aring;', 'Å')
    raw_text = raw_text.replace('&AElig;', 'Æ')
    raw_text = raw_text.replace('&Ccedil;', 'Ç')
    raw_text = raw_text.replace('&Egrave;', 'È')
    raw_text = raw_text.replace('&Eacute;', 'É')
    raw_text = raw_text.replace('&Ecirc;', 'Ê')
    raw_text = raw_text.replace('&Euml;', 'Ë')
    raw_text = raw_text.replace('&Igrave;', 'Ì')
    raw_text = raw_text.replace('&Iacute;', 'Í')
    raw_text = raw_text.replace('&Icirc;', 'Î')
    raw_text = raw_text.replace('&Iuml;', 'Ï')
    raw_text = raw_text.replace('&ETH;', 'Ð')
    raw_text = raw_text.replace('&Ntilde;', 'Ñ')
    raw_text = raw_text.replace('&Ograve;', 'Ò')
    raw_text = raw_text.replace('&Oacute;', 'Ó')
    raw_text = raw_text.replace('&Ocirc;', 'Ô')
    raw_text = raw_text.replace('&Otilde;', 'Õ')
    raw_text = raw_text.replace('&Ouml;', 'Ö')
    raw_text = raw_text.replace('&Oslash;', 'Ø')
    raw_text = raw_text.replace('&Ugrave;', 'Ù')
    raw_text = raw_text.replace('&Uacute;', 'Ú')
    raw_text = raw_text.replace('&Ucirc;', 'Û')
    raw_text = raw_text.replace('&Uuml;', 'Ü')
    raw_text = raw_text.replace('&Yacute;', 'Ý')
    raw_text = raw_text.replace('&THORN;', 'Þ')
    raw_text = raw_text.replace('&szlig;', 'ß')
    raw_text = raw_text.replace('&agrave;', 'à')
    raw_text = raw_text.replace('&aacute;', 'á')
    raw_text = raw_text.replace('&acirc;', 'â')
    raw_text = raw_text.replace('&atilde;', 'ã')
    raw_text = raw_text.replace('&auml;', 'ä')
    raw_text = raw_text.replace('&aring;', 'å')
    raw_text = raw_text.replace('&aelig;', 'æ')
    raw_text = raw_text.replace('&ccedil;', 'ç')
    raw_text = raw_text.replace('&egrave;', 'è')
    raw_text = raw_text.replace('&eacute;', 'é')
    raw_text = raw_text.replace('&ecirc;', 'ê')
    raw_text = raw_text.replace('&euml;', 'ë')
    raw_text = raw_text.replace('&igrave;', 'ì')
    raw_text = raw_text.replace('&iacute;', 'í')
    raw_text = raw_text.replace('&icirc;', 'î')
    raw_text = raw_text.replace('&iuml;', 'ï')
    raw_text = raw_text.replace('&eth;', 'ð')
    raw_text = raw_text.replace('&ntilde;', 'ñ')
    raw_text = raw_text.replace('&ograve;', 'ò')
    raw_text = raw_text.replace('&oacute;', 'ó')
    raw_text = raw_text.replace('&ocirc;', 'ô')
    raw_text = raw_text.replace('&otilde;', 'õ')
    raw_text = raw_text.replace('&ouml;', 'ö')
    raw_text = raw_text.replace('&oslash;', 'ø')
    raw_text = raw_text.replace('&ugrave;', 'ù')
    raw_text = raw_text.replace('&uacute;', 'ú')
    raw_text = raw_text.replace('&ucirc;', 'û')
    raw_text = raw_text.replace('&uuml;', 'ü')
    raw_text = raw_text.replace('&yacute;', 'ý')
    raw_text = raw_text.replace('&thorn;', 'þ')
    raw_text = raw_text.replace('&yuml;', 'ÿ')
    raw_text = raw_text.replace('&nbsp;', ' ')
    raw_text = raw_text.replace('&iexcl;', '¡')
    raw_text = raw_text.replace('&cent;', '¢')
    raw_text = raw_text.replace('&pound;', '£')
    raw_text = raw_text.replace('&curren;', '¤')
    raw_text = raw_text.replace('&yen;', '¥')
    raw_text = raw_text.replace('&brvbar;', '¦')
    raw_text = raw_text.replace('&sect;', '§')
    raw_text = raw_text.replace('&uml;', '¨')
    raw_text = raw_text.replace('&copy;', '©')
    raw_text = raw_text.replace('&ordf;', 'ª')
    raw_text = raw_text.replace('&laquo;', '«')
    raw_text = raw_text.replace('&not;', '¬')
    raw_text = raw_text.replace('&shy;', '­')
    raw_text = raw_text.replace('&reg;', '®')
    raw_text = raw_text.replace('&macr;', '¯')
    raw_text = raw_text.replace('&deg;', '°')
    raw_text = raw_text.replace('&plusmn;', '±')
    raw_text = raw_text.replace('&sup2;', '²')
    raw_text = raw_text.replace('&sup3;', '³')
    raw_text = raw_text.replace('&acute;', '´')
    raw_text = raw_text.replace('&micro;', 'µ')
    raw_text = raw_text.replace('&para;', '¶')
    raw_text = raw_text.replace('&cedil;', '¸')
    raw_text = raw_text.replace('&sup1;', '¹')
    raw_text = raw_text.replace('&ordm;', 'º')
    raw_text = raw_text.replace('&raquo;', '»')
    raw_text = raw_text.replace('&frac14;', '¼')
    raw_text = raw_text.replace('&frac12;', '½')
    raw_text = raw_text.replace('&frac34;', '¾')
    raw_text = raw_text.replace('&iquest;', '¿')
    raw_text = raw_text.replace('&times;', '×')
    raw_text = raw_text.replace('&divide;', '÷')
    raw_text = raw_text.replace('&forall;', '∀')
    raw_text = raw_text.replace('&part;', '∂')
    raw_text = raw_text.replace('&exist;', '∃')
    raw_text = raw_text.replace('&empty;', '∅')
    raw_text = raw_text.replace('&nabla;', '∇')
    raw_text = raw_text.replace('&isin;', '∈')
    raw_text = raw_text.replace('&notin;', '∉')
    raw_text = raw_text.replace('&ni;', '∋')
    raw_text = raw_text.replace('&prod;', '∏')
    raw_text = raw_text.replace('&sum;', '∑')
    raw_text = raw_text.replace('&minus;', '−')
    raw_text = raw_text.replace('&lowast;', '∗')
    raw_text = raw_text.replace('&radic;', '√')
    raw_text = raw_text.replace('&prop;', '∝')
    raw_text = raw_text.replace('&infin;', '∞')
    raw_text = raw_text.replace('&ang;', '∠')
    raw_text = raw_text.replace('&and;', '∧')
    raw_text = raw_text.replace('&or;', '∨')
    raw_text = raw_text.replace('&cap;', '∩')
    raw_text = raw_text.replace('&cup;', '∪')
    raw_text = raw_text.replace('&int;', '∫')
    raw_text = raw_text.replace('&there4;', '∴')
    raw_text = raw_text.replace('&sim;', '∼')
    raw_text = raw_text.replace('&cong;', '≅')
    raw_text = raw_text.replace('&asymp;', '≈')
    raw_text = raw_text.replace('&ne;', '≠')
    raw_text = raw_text.replace('&equiv;', '≡')
    raw_text = raw_text.replace('&le;', '≤')
    raw_text = raw_text.replace('&ge;', '≥')
    raw_text = raw_text.replace('&sub;', '⊂')
    raw_text = raw_text.replace('&sup;', '⊃')
    raw_text = raw_text.replace('&nsub;', '⊄')
    raw_text = raw_text.replace('&sube;', '⊆')
    raw_text = raw_text.replace('&supe;', '⊇')
    raw_text = raw_text.replace('&oplus;', '⊕')
    raw_text = raw_text.replace('&otimes;', '⊗')
    raw_text = raw_text.replace('&perp;', '⊥')
    raw_text = raw_text.replace('&sdot;', '⋅')
    raw_text = raw_text.replace('&Alpha;', 'Α')
    raw_text = raw_text.replace('&Beta;', 'Β')
    raw_text = raw_text.replace('&Gamma;', 'Γ')
    raw_text = raw_text.replace('&Delta;', 'Δ')
    raw_text = raw_text.replace('&Epsilon;', 'Ε')
    raw_text = raw_text.replace('&Zeta;', 'Ζ')
    raw_text = raw_text.replace('&Eta;', 'Η')
    raw_text = raw_text.replace('&Theta;', 'Θ')
    raw_text = raw_text.replace('&Iota;', 'Ι')
    raw_text = raw_text.replace('&Kappa;', 'Κ')
    raw_text = raw_text.replace('&Lambda;', 'Λ')
    raw_text = raw_text.replace('&Mu;', 'Μ')
    raw_text = raw_text.replace('&Nu;', 'Ν')
    raw_text = raw_text.replace('&Xi;', 'Ξ')
    raw_text = raw_text.replace('&Omicron;', 'Ο')
    raw_text = raw_text.replace('&Pi;', 'Π')
    raw_text = raw_text.replace('&Rho;', 'Ρ')
    raw_text = raw_text.replace('&Sigma;', 'Σ')
    raw_text = raw_text.replace('&Tau;', 'Τ')
    raw_text = raw_text.replace('&Upsilon;', 'Υ')
    raw_text = raw_text.replace('&Phi;', 'Φ')
    raw_text = raw_text.replace('&Chi;', 'Χ')
    raw_text = raw_text.replace('&Psi;', 'Ψ')
    raw_text = raw_text.replace('&Omega;', 'Ω')
    raw_text = raw_text.replace('&alpha;', 'α')
    raw_text = raw_text.replace('&beta;', 'β')
    raw_text = raw_text.replace('&gamma;', 'γ')
    raw_text = raw_text.replace('&delta;', 'δ')
    raw_text = raw_text.replace('&epsilon;', 'ε')
    raw_text = raw_text.replace('&zeta;', 'ζ')
    raw_text = raw_text.replace('&eta;', 'η')
    raw_text = raw_text.replace('&theta;', 'θ')
    raw_text = raw_text.replace('&iota;', 'ι')
    raw_text = raw_text.replace('&kappa;', 'κ')
    raw_text = raw_text.replace('&lambda;', 'λ')
    raw_text = raw_text.replace('&mu;', 'μ')
    raw_text = raw_text.replace('&nu;', 'ν')
    raw_text = raw_text.replace('&xi;', 'ξ')
    raw_text = raw_text.replace('&omicron;', 'ο')
    raw_text = raw_text.replace('&pi;', 'π')
    raw_text = raw_text.replace('&rho;', 'ρ')
    raw_text = raw_text.replace('&sigmaf;', 'ς')
    raw_text = raw_text.replace('&sigma;', 'σ')
    raw_text = raw_text.replace('&tau;', 'τ')
    raw_text = raw_text.replace('&upsilon;', 'υ')
    raw_text = raw_text.replace('&phi;', 'φ')
    raw_text = raw_text.replace('&chi;', 'χ')
    raw_text = raw_text.replace('&psi;', 'ψ')
    raw_text = raw_text.replace('&omega;', 'ω')
    raw_text = raw_text.replace('&thetasym;', 'ϑ')
    raw_text = raw_text.replace('&upsih;', 'ϒ')
    raw_text = raw_text.replace('&piv;', 'ϖ')
    raw_text = raw_text.replace('&OElig;', 'Œ')
    raw_text = raw_text.replace('&oelig;', 'œ')
    raw_text = raw_text.replace('&Scaron;', 'Š')
    raw_text = raw_text.replace('&scaron;', 'š')
    raw_text = raw_text.replace('&Yuml;', 'Ÿ')
    raw_text = raw_text.replace('&fnof;', 'ƒ')
    raw_text = raw_text.replace('&circ;', 'ˆ')
    raw_text = raw_text.replace('&tilde;', '˜')
    raw_text = raw_text.replace('&ensp;', ' ')
    raw_text = raw_text.replace('&emsp;', ' ')
    raw_text = raw_text.replace('&thinsp;', ' ')
    raw_text = raw_text.replace('&ndash;', '–')
    raw_text = raw_text.replace('&mdash;', '—')
    raw_text = raw_text.replace('&lsquo;', '‘')
    raw_text = raw_text.replace('&rsquo;', '’')
    raw_text = raw_text.replace('&sbquo;', '‚')
    raw_text = raw_text.replace('&ldquo;', '“')
    raw_text = raw_text.replace('&rdquo;', '”')
    raw_text = raw_text.replace('&bdquo;', '„')
    raw_text = raw_text.replace('&dagger;', '†')
    raw_text = raw_text.replace('&Dagger;', '‡')
    raw_text = raw_text.replace('&bull;', '•')
    raw_text = raw_text.replace('&hellip;', '…')
    raw_text = raw_text.replace('&permil;', '‰')
    raw_text = raw_text.replace('&prime;', '′')
    raw_text = raw_text.replace('&Prime;', '″')
    raw_text = raw_text.replace('&lsaquo;', '‹')
    raw_text = raw_text.replace('&rsaquo;', '›')
    raw_text = raw_text.replace('&oline;', '‾')
    raw_text = raw_text.replace('&euro;', '€')
    raw_text = raw_text.replace('&trade;', '™')
    raw_text = raw_text.replace('&larr;', '←')
    raw_text = raw_text.replace('&uarr;', '↑')
    raw_text = raw_text.replace('&rarr;', '→')
    raw_text = raw_text.replace('&darr;', '↓')
    raw_text = raw_text.replace('&harr;', '↔')
    raw_text = raw_text.replace('&crarr;', '↵')
    raw_text = raw_text.replace('&lceil;', '⌈')
    raw_text = raw_text.replace('&rceil;', '⌉')
    raw_text = raw_text.replace('&lfloor;', '⌊')
    raw_text = raw_text.replace('&rfloor;', '⌋')
    raw_text = raw_text.replace('&loz;', '◊')
    raw_text = raw_text.replace('&spades;', '♠')
    raw_text = raw_text.replace('&clubs;', '♣')
    raw_text = raw_text.replace('&hearts;', '♥')
    raw_text = raw_text.replace('&diams;', '♦')
    raw_text = raw_text.replace('&weierp;', '℘')
    raw_text = raw_text.replace('( or, Greek: Ασχύλος, Aiskhylos', '(Greek: Ασχύλος, Aiskhylos')
    raw_text = raw_text.replace(' (Akkadian: ; Arabic: ; Hebrew:, Aramaic: )', '')
    raw_text = raw_text.replace(' Several people bore the name:\\n\\nA descendant', '\\n\\nSeveral people bore the name: A descendant')
    raw_text = raw_text.replace('(Icelandic for "Æsir faith",, in Old Norse ;', '(Icelandic for "Æsir faith",')
    raw_text = raw_text.replace('Saint Adalbert, Czech: ;, (c. 956 – April 23, 997)', 'Saint Adalbert, Czech:, (c. 956 – April 23, 997)')
    raw_text = raw_text.replace('Zermelo-Fraenkel set theory and was introduced by .', 'Zermelo-Fraenkel set theory.')
    raw_text = raw_text.replace('Dutch personal/home computer. . The Aster computer', 'Dutch personal/home computer. The Aster computer')
    raw_text = raw_text.replace('(Greek: [aí.jo.los], Ailos Modern Greek:)', '(Greek: [aí.jo.los], Ailos)')
    raw_text = raw_text.replace('(in Greek,, "daughter of Atlas")', '(in Greek, "daughter of Atlas")')
    raw_text = raw_text.replace('"to write",, is a biography', '"to write", is a biography')
    raw_text = raw_text.replace('For examples of Jewish-Arab dialogue see Projects working for peace among Israelis and Arabs\\n\\nAntisemitism', 'Antisemitism')
    raw_text = raw_text.replace(' ( = OH-weh)', '')
    raw_text = raw_text.replace('(;, ASG)', '(ASG)')
    raw_text = raw_text.replace(' (—, conventional short form )', '')
    raw_text = raw_text.replace('except in certain gamete stages. This is a diverse group', 'except in certain gamete stages.\\n\\nThis is a diverse group')
    raw_text = raw_text.replace('(also Aelle or Ella, )', '(also Aelle or Ella)')
    raw_text = raw_text.replace(' (abbreviated )', '')
    raw_text = raw_text.replace('<ref name=Restorer></ref>', '')
    if raw_text.startswith('thumbthumbthumbthumbA'):
      raw_text = raw_text[20:]
    raw_text = raw_text.replace(' (born )', '')
    if raw_text.startswith('is a nickname for a military base located in the southern'):
      raw_text = 'Area 51 ' + raw_text
    raw_text = raw_text.replace(' ( in the Quechua language)', '')
    if raw_text.startswith('This article is about the chemical compounds alkaloids.'):
      raw_text = raw_text[147:]
    raw_text = raw_text.replace('club from Rome, . Founded', 'club from Rome. Founded')
    if raw_text.startswith('</div>'):
      raw_text = raw_text[6:]
    raw_text = raw_text.replace(" (or Oh' jeh)", "")
    raw_text = raw_text.replace('( (full title: Al-Sultan', '(full title: Al-Sultan')
    raw_text = raw_text.replace(' ( – )', '')
    raw_text = raw_text.replace('(German ; rarely anglicized Argovia)', '(rarely anglicized Argovia)')
    raw_text = raw_text.replace('( "ah buh KAH")', '("ah buh KAH")')
    raw_text = raw_text.replace('(; Khakass: Ағбан)', '(Khakass: Ағбан)')
    raw_text = raw_text.replace('(; ; ; ; ; ', '(')
    raw_text = raw_text.replace('(; ; ; ; ', '(')
    raw_text = raw_text.replace('(; ; ; ', '(')
    raw_text = raw_text.replace('(; ; ', '(')
    raw_text = raw_text.replace('(; ', '(')
    if raw_text.startswith(' is a large public square and transport hub in the Mitte'):
      raw_text = 'Alexanderplatz' + raw_text
    raw_text = raw_text.replace('a single number, the sum. The set of natural numbers', 'a single number, the sum.\\n\\nThe set of natural numbers')
    raw_text = raw_text.replace(' ( June 11 1970)', '')
    raw_text = raw_text.replace('temple.thumbMany', 'temple. Many')
    raw_text = raw_text.replace('Trapani, with a total area of .', 'Trapani.')
    raw_text = raw_text.replace(' (;, ; ;, )', '')
    if raw_text.startswith('This article is about a city in central Rajasthan, for the historical region'):
      raw_text = raw_text[95:]
    if raw_text.startswith('For the British submarine see HMS Affray (P421)'):
      raw_text = raw_text[51:]
    raw_text = raw_text.replace(' (Talmudic Aramaic: )', '')
    raw_text = raw_text.replace(' <200e>', '')
    raw_text = raw_text.replace('Allāh; ; January', 'Allāh; January')
    if raw_text.startswith('left'):
      raw_text = raw_text[4:]
    raw_text = raw_text.replace('Abigail. There appear to be two individuals named Abigail:', 'Abigail.\\n\\nThere appear to be two individuals named Abigail:')
    raw_text = raw_text.replace(' ( or )', '')
    raw_text = raw_text.replace("'''", "")
    raw_text = raw_text.replace(' (Devanagari: ; IAST )', '')
    raw_text = raw_text.replace(' ( in English, in Spanish)', '')
    raw_text = raw_text.replace('right or privilege. It comes', 'right or privilege. (It comes')
    raw_text = raw_text.replace('Tāzī . Other', 'Tāzī. Other')
    return raw_text
    



def main(_argv):
  """The entrypoint for the script"""

  # Check for existence of required flags
  if not FLAGS.output_dir:
    raise ValueError("You must specify output_dir")
  if not FLAGS.wex_articles:
    raise ValueError("You must specify wex_articles")

  # Generate WEX corpus
  wexCorpusGenerator = WEXCorpusGenerator(FLAGS.output_dir, FLAGS.wex_articles)
  wexCorpusGenerator.run()

if __name__ == "__main__":
  tf.logging.set_verbosity(tf.logging.INFO)
  tf.app.run()
