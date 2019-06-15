# -*- coding: utf-8 -*-

#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this file. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright © 2016-2019 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test the SamediggiNoPage class."""
import os
import unittest

import requests
import requests_mock

from corpustools import samediggi_no_crawler

HERE = os.path.dirname(__file__)

MY_TEXT = '''
<!DOCTYPE html>
  <html lang="se-NO">
  <head>
      <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
       <title>      PRD: Doarjja julevsámi giellaprošeavttaide
  </title>
    <meta name="description" content="" />
                                    <meta name="Content-language" content="sme-NO" />

    <!-- open graph social meta -->

                      <link rel="alternate" type="application/rss+xml" href="https://samediggi.no/rss" />

      <!-- styling -->
          <link rel="stylesheet" href="/css/72d9e06.css" />


    <!-- javascripts -->
    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
<!-- WARNING: Respond.js doesn\'t work if you view the page via file:// -->
<!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->

<!-- jQuery (necessary for Bootstrap\'s JavaScript plugins) -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
<!-- Include all compiled plugins (below), or include individual files as needed -->


  <script src="/js/ca237f5.js"></script>


    <script type="text/javascript">

        var _gaq = _gaq || [];
        _gaq.push([\'_setAccount\', \'UA-13172157-1\']);
        _gaq.push([\'_trackPageview\']);

        (function() {
            var ga = document.createElement(\'script\'); ga.type = \'text/javascript\'; ga.async = true;
            ga.src = (\'https:\' == document.location.protocol ? \'https://ssl\' : \'http://www\') + \'.google-analytics.com/ga.js\';
            var s = document.getElementsByTagName(\'script\')[0]; s.parentNode.insertBefore(ga, s);
        })();

    </script>




    <link rel="icon" href="/favicon.ico?v=2" />

    </head>

    <!--
      layoutOrange     -->



  <body class="layoutOrange">

  <!-- start header -->
  <header>

<div class="row menuSearchForm">
  <div class="col-lg-6 col-lg-offset-3">
    <form class="searchForms" action="/Soek" method="get">
      <div class="input-group">
        <input type="text" name="search" class="form-control searchFormsInput" placeholder="Oza neahttabáikkis, dokumeanttain ja áššiin" required="required" />
        <span class="input-group-btn">
          <button class="btn searchFormsButton">
            <span class="customIcon2 customIcon-search" aria-hidden="true"></span>
          </button>
        </span>
      </div>
    </form>
  </div>
</div>


<div
  class="header "

  >

  <nav class="navbar navbar-default customTopNavBar">
    <div class="container">

      <div class="topMenu">

        <div class="subToplogo">
          <a href="/">
                        <img src="/bundles/sametingetsite/images/sam-logo.jpg" alt="Logo"/>
          </a>
        </div>

        <div class="subtopMenuRight">
          <ul class="nav navbar-nav">
            <li class="itemLanguage">
              <div class="dropdown">
                <a href="#" class="customIcon2 customIcon-arrowDown" id="dropdownMenu1" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
                Davvisámegillii
                </a>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                                                                                                <li><a href="//www.sametinget.no/Nyhetsarkiv/parallel1">Norsk</a></li>
                                                                                                                                      <li><a href="//www.saemiedigkie.no/Saernievaaarhkoe/parallel1">Åarjelsaemiengïelese</a></li>
                                                                                                                                      <li><a href="//www.samedigge.no/AAdaasa/PRD-Doarjju-julevsame-giellaprosjevtajda">Julevsámegiella</a></li>
                                                                      </ul>
              </div>
            </li>

            <li class="itemLogin"></li>
            <li class="itemSearch">
              <a class="customIcon2 customIcon-search searchOpen" href="#">Oza</a>
            </li>
            <li class="itemMenu">
              <a class="customIcon2 customIcon-menu showMegaMenu" href="#">
                <span class="textOpen">Meny</span>
                <span class="textClose">Gidde</span>
              </a>
            </li>
          </ul>
        </div>
      </div>

    </div>
  </nav>



        <div class="newsIntro">
      <div class="container">
        <div class="row">
          <div class="col-md-6 col-lg-6 col-md-offset-3 col-lg-offset-3 ">
            <div class="newsIntroBox">
                    <h1>PRD: Doarjja julevsámi giellaprošeavttaide</h1>
        <div class="introContent"><div class="ezrichtext-field"><p>S&aacute;medigger&aacute;&#273;&#273;i juolluda doarjaga guovtti julevs&aacute;megiel giellapro&scaron;ektii. Giellaspeallu New Amigos Online h&aacute;bmejuvvo julevs&aacute;megillii, ja Divttasvuona oahppit &#269;ohkkejuvvojit Johkamohkk&aacute;i giellal&aacute;vgumii. &ndash; Julevs&aacute;megiella d&aacute;rbba&scaron;a arenaid gos giellageavaheaddjit besset s&aacute;m&aacute;stit, dadj&aacute; s&aacute;mediggepresideanta Aili Keskitalo.</p>
</div>
</div>

      <div class="date">
      <p>
        Ođas |
                  Almmuhuvvon <time datetime="2019-06-11">11.6.2019</time>
              </p>
    </div>

            </div>
          </div>
        </div>
      </div>
    </div>

  <div class="container">

    <div class="row">
    <div class="col-md-12 col-lg-12">

       <div class="row megaMenuContent">
         <div class="col-md-12 visible-sm-block visible-xs-block">
           <form class="searchForms" action="/Soek" method="get">
             <div class="input-group">
                 <input type="text" name="search" class="form-control searchFormsInput" placeholder="Oza neahttabáikkis, dokumeanttain ja áššiin" required="required" />
                <span class="input-group-btn">
                    <button class="btn searchFormsButton">
                      <span class="customIcon2 customIcon-search" aria-hidden="true"></span>
                    </button>
                </span>
              </div>
           </form>
         </div>

        <div class="col-md-5 col-md-offset-1">
          <ul class="nav primaryMenu">
               <li><a href="/Balvalusat2/Giella">Giella</a></li>
  <li><a href="/Balvalusat2/Manaidgardi">Mánáidgárdi</a></li>
  <li><a href="/Balvalusat2/Kultuvra">Kultuvra </a></li>
  <li><a href="/Balvalusat2/Oahpahus-ja-oahpponeavvut">Oahpahus ja oahpponeavvut</a></li>
  <li><a href="/Balvalusat2/Ealahusat">Ealáhusat</a></li>
  <li><a href="/Balvalusat2/Dearvvasvuohta-ja-sosiala">Dearvvašvuohta ja sosiála</a></li>
  <li><a href="/Balvalusat2/Biras-areala-ja-kultursuodjaleapmi">Biras, areála ja kultursuodjaleapmi</a></li>
  <li><a href="/Balvalusat2/Riikkaidgaskasas-bargu">Riikkaidgaskasaš bargu</a></li>
  <li><a href="/Balvalusat2/Dassearvu">Dásseárvu</a></li>
  <li><a href="/Girjeradju">Girjerádju</a></li>

          </ul>
        </div>
        <div class="col-md-5">
          <ul class="nav secondaryMenu">

               <li><a href="/Doarjagat-ja-stipeanddat">Doarjagat ja stipeanddat</a></li>
  <li><a href="/Vuoigatvuodat">Vuoigatvuođat</a></li>
  <li><a href="/Lagideamit">Lágideamit</a></li>
  <li><a href="/Politihkka2/Assit-ja-dokumeanttat">Áššit ja dokumeanttat</a></li>
  <li><a href="/Politihkka2">Politihkka</a></li>
  <li><a href="/Valga">Válga</a></li>
  <li><a href="/Samedikki-birra">Sámedikki birra</a></li>
  <li><a href="/Preassa">Preassa</a></li>
  <li><a href="/Odasarkiiva">Ođasarkiiva</a></li>


            <!-- Show only mobile -->
            <li class="showMobile">
              <div class="dropdown">
                <a href="#" class="customIcon2 customIcon-arrowDown" id="dropdownMenu2" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
                  Davvisámegillii
                </a>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenu2">
                                                                                                  <li><a href="//www.sametinget.no/Nyhetsarkiv/parallel1">Norsk</a></li>
                                                                                                                                      <li><a href="//www.saemiedigkie.no/Saernievaaarhkoe/parallel1">Åarjelsaemiengïelese</a></li>
                                                                                                                                      <li><a href="//www.samedigge.no/AAdaasa/PRD-Doarjju-julevsame-giellaprosjevtajda">Julevsámegiella</a></li>
                                                                      </ul>
              </div>
            </li>
          </ul>
        </div>
      </div>

     </div>

    </div>
  </div>



</div>      </header>
  <!-- end header -->

  <!-- start breadcrumb -->
      <div class="breadcrumbWrapper">
    <div class="container">
      <div class="row">
        <div class="col-md-6 col-lg-6 col-md-offset-3 col-lg-offset-3">
                    <ol class="breadcrumb">
                                          <li><a href="/">Sámediggi</a></li>
                                                        <li><a href="/Odasarkiiva">Ođasarkiiva</a></li>
                                                        <li class="active"><span>PRD: Doarjja julevsámi giellaprošeavttaide</span></li>
                                    </ol>
        </div>
      </div>
    </div>
  </div>

  <!-- end breadcrumb -->

  <!-- start content -->
  <div class="mainContent ">
      <section class="articleWrapper">
    <div class="container">
      <div class="row">
        <div class="col-md-6 col-lg-6 col-md-offset-3 col-lg-offset-3">
          <article class="article">
                          <div class="ezrichtext-field"><p>S&aacute;medigger&aacute;&#273;&#273;i juolluda 300.000 ruvdnosa&scaron; doarjaga NA TECHNOLOGIES DA:i h&aacute;bmet giellaspealu New Amigos Online julevs&aacute;megillii. Dat lea virtu&aacute;la s&aacute;megielat arena gos giela praktisere ovttasbargguin. Dasa lassin dan lea vejola&scaron; speallat okto (single-player mode), mas speallit s&aacute;httet videob&aacute;ddemiiguin h&aacute;rjehallat. Videob&aacute;ddemiidda leat b&aacute;ddejuvvon ie&scaron;gu&#273;etge suopmaniid eatnigielh&aacute;llit.</p><p><strong>&ndash; S&aacute;megielaid doaibmapl&aacute;nas boaht&aacute; ovdan ahte lea d&aacute;rbu eatnigielat digit&aacute;la oahpporesurssaide s&aacute;mi m&aacute;n&aacute;ide ja nuoraide. New Amigos lea som&aacute;s guovttegielat speallu mii heive ie&scaron;gu&#273;etge ahk&aacute;ha&#269;&#269;aide, dadj&aacute; Keskitalo.</strong></p><p>New Amigos Online heiveha oktagasla&scaron; oahppama ovttasdoaibmama bokte neahtas. Studeanttat doibmet resursan guhtet guimmiidasaset ja skuvladilis oahpaheaddji heiveha nu, ahte New Amigos Online dievasmahtt&aacute; ear&aacute; oahpahusa. V&aacute;s&aacute;hus &scaron;add&aacute; persovnnala&#382;&#382;an ja f&aacute;tmmasteaddjin go oahppit olles riikkas ja m&aacute;ilmmis besset gulahallat neahtas.</p><p><strong>&ndash; S&aacute;mediggi atn&aacute; d&aacute;rbba&scaron;la&#382;&#382;an h&aacute;bmet digit&aacute;la giellaapplika&scaron;uvnnaid julevs&aacute;megillii nannen dihtii giela, eandalii guovlluin gos giella lea ra&scaron;is dilis.</strong></p><h3>Julevs&aacute;megiela giellal&aacute;vgun</h3><p>S&aacute;medigger&aacute;&#273;&#273;i juolluda maidd&aacute;i 160.000 ruvdnosa&scaron; doarjaga Divttasvuona suohkanii Giellabiesse 2019-pro&scaron;ektii, mas ulbmilin lea &#269;ohkket ohppiid julevs&aacute;megiela giellal&aacute;vgumii.</p><p>D&aacute;n jag&aacute;&scaron; Giellabiesse lea Johkamohkis, Ruo&#359;a bealde. D&aacute;n giellal&aacute;vguma v&aacute;ldomihttun lea &#269;iek&#331;ut boazodoallo- ja meahc&aacute;standoahpagiidda ja -fr&aacute;saide. Doppe oahpahuvvojit maidd&aacute;i &aacute;rgabeaigiela vuo&#273;&#273;ofr&aacute;sat. Dan vahku f&aacute;dd&aacute;n lea oahp&aacute;smuvvat Sirg&aacute;sa &#269;earu meahc&aacute;stan- ja boazodoallokultuvrii ja oahp&aacute;smuvvat s&aacute;mekultuvrii nuppe bealde r&aacute;ji.</p><p><strong>&ndash; Giellabiesse lea buorre ja deh&aacute;la&scaron; gielladoaibma julevs&aacute;mi guovllus. Giella lea ra&scaron;&scaron;i d&aacute;n guovllus ja buot diekk&aacute;r doaimmain lea positiivvala&scaron; v&aacute;ikkuhus s&aacute;megillii. Diibm&aacute; sis lei sullasa&scaron; Giellabiesse, muhto dalle fitne Johkamohki oahppit &Aacute;jluovttas. Raporttas oaidnit ahte d&aacute;t l&aacute;gideapmi lihkostuvai, dadj&aacute; s&aacute;mediggepresideanta Aili Keskitalo.</strong></p><p><em>Oktavuo&#273;adie&#273;ut:</em></p><p><em>S&aacute;mediggepresideanta Aili Keskitalo, tlf. +47 971 29 305</em></p>
</div>

                      </article>
        </div>
      </div>
    </div>
  </section>


  </div>
  <!-- end content -->

  <!-- start contact -->
      <section class="contact">
      <div class="container">
        <div class="row">
          <div class="col-md-8 col-md-offset-2 col-lg-8 col-lg-offset-2">
            <div class="contactContent">
              <div class="contactTitle">
                <h4>Gávdnet go dan maid ohcet?</h4>
              </div>
                <div class="contactButtons">
                  <form class="feedback" method="post" action="/feedback" id="feedbackAnswer">
                    <input type="hidden" name="content_id" value="3258" />
                    <button type="button" class="btn btn-orange showContactForms" value="1">Juo</button>
                    <button type="button" class="btn btn-green showContactForms" value="0">In</button>
                    </form>
                 </div>

              <div class="contactForms">
                <p>Hva lette du etter? Din tilbakemelding hjelper oss ålage bedre nettsider.</p>
                <form class="feedback" method="post" action="/feedback" id="feedbackComment">
                  <div class="form-group">
                     <textarea name="comment" class="form-control" rows="6"></textarea>
                  </div>

                  <button type="submit" class="btn btn-orange">Send</button>
                </form>
              </div>
              <div class="contactMessage">
                <h4>Takk for din tilbakemelding!</h4>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

  <!-- end contact -->

  <!-- start footer -->
  <footer class="mainFooter">
    <div class="container">
    <div class="row">
      <div class="col-md-12 col-lg-12">
                  <h3>Sámediggi</h3>

        <div class="info">
                                <p><span aria-hidden="true">Orgnr. 974760347</span> </p>

                      <p><span class="customIcon customIcon-mapPoint" aria-hidden="true">Ávjovárgeaidnu 50, 9730 Kárášjohka</span> </p>

                      <p><span class="customIcon customIcon-phone" aria-hidden="true">+ 47 78 47 40 00</span> </p>

                      <p><span class="customIcon customIcon-mail" aria-hidden="true">
              <a href="mailto:samediggi@samediggi.no">samediggi@samediggi.no</a>
            </span> </p>

                                <p><a href="/Samedikki-birra2/Rehket-Samediggai">Rehket Sámediggái</a></p>

                                <p><a href="/Samedikki-birra2/langlink">Mátkerehkegat ja buhtadusgáibádusat Sámediggái</a></p>
                  </div>

                  <h4>Čuovo min sosiála mediain</h4>

        <div class="info">
            <p>
                              <span class="customIcon customIcon-facebook" aria-hidden="true">
                  <a href="https://www.facebook.com/samediggi">Facebook</a>
                </span>

                              <span class="customIcon customIcon-twitter" aria-hidden="true">
                  <a href="https://twitter.com/samediggi">Twitter</a>
                </span>

                              <span class="customIcon customIcon-instagram" aria-hidden="true">
                  <a href="https://www.instagram.com/samediggi/">Instagram</a>
                </span>

            </p>
        </div>

        <ul class="footerLinks">
                      <li> <a href="/Samedikki-birra2/langlink2">Váldde oktavuođa Sámedikkiin: Bargit ja kantuvrrat</a> </li>
                                <li> <a href="/Doarjagat-ja-stipeanddat">Doarjagat ja stipeanddat</a> </li>
                  </ul>

        <div class="cookiesInfo">
          <p>Vi bruker cookies. For mer informasjon.
                      <a href="#"> se vår cookies policy</a>
                    </p>
        </div>
      </div>
    </div>
  </div>
  </footer>
  <!-- end footer -->

    <!-- footer javascript -->



  </body>
</html>'''


class TestSamediggiNoPage(unittest.TestCase):
    """Test the SamediggiNoPage class."""

    def test_basics(self):
        """Test initial values."""
        with requests_mock.Mocker() as mocker:
            mocker.get(
                'https://samediggi.no/Odasarkiiva/PRD-Doarjja-julevsami-giellaproseavttaide',
                text=MY_TEXT,
                headers={'content-type': 'text/html; charset=UTF-8'})
            result = requests.get(
                'https://samediggi.no/Odasarkiiva/PRD-Doarjja-julevsami-giellaproseavttaide'
            )

            page = samediggi_no_crawler.SamediggiNoPage(result, {})
            self.assertEqual(
                page.corpuspath.orig,
                os.path.join(
                    os.getenv('GTFREE'),
                    'orig/sme/admin/sd/samediggi.no/prd-doarjja-julevsami-giellaproseavttaide.html'
                ))
            self.assertEqual(
                page.url,
                'https://samediggi.no/Odasarkiiva/PRD-Doarjja-julevsami-giellaproseavttaide'
            )
            self.assertListEqual(page.parallel_links, [
                'https://www.sametinget.no/Nyhetsarkiv/parallel1',
                'https://www.saemiedigkie.no/Saernievaaarhkoe/parallel1',
                'https://www.samedigge.no/AAdaasa/PRD-Doarjju-julevsame-giellaprosjevtajda'
            ])
            self.assertTrue(page.saveable)
            self.assertEqual(page.lang, 'sme')
            self.assertSetEqual(
                page.links,
                set([
                    'https://samediggi.no/Balvalusat2/Dearvvasvuohta-ja-sosiala',
                    'https://samediggi.no/Vuoigatvuodat',
                    'https://samediggi.no/Samedikki-birra2/Rehket-Samediggai',
                    'https://samediggi.no/Samedikki-birra',
                    'https://samediggi.no/Doarjagat-ja-stipeanddat',
                    'https://samediggi.no/Preassa',
                    'https://samediggi.no/Samedikki-birra2/langlink',
                    'https://samediggi.no/Balvalusat2/Ealahusat',
                    'https://samediggi.no/Politihkka2/Assit-ja-dokumeanttat',
                    'https://samediggi.no/Odasarkiiva',
                    'https://samediggi.no/Balvalusat2/Giella',
                    'https://samediggi.no/Samedikki-birra2/langlink2',
                    'https://samediggi.no/Balvalusat2/Kultuvra',
                    'https://samediggi.no/Valga',
                    'https://samediggi.no/Balvalusat2/Dassearvu',
                    'https://samediggi.no/Politihkka2',
                    'https://samediggi.no/Lagideamit',
                    'https://samediggi.no/Balvalusat2/Oahpahus-ja-oahpponeavvut',
                    'https://samediggi.no/Balvalusat2/Riikkaidgaskasas-bargu',
                    'https://samediggi.no/Girjeradju',
                    'https://samediggi.no/Balvalusat2/Biras-areala-ja-kultursuodjaleapmi',
                    'https://samediggi.no/Balvalusat2/Manaidgardi'
                ]))

            page.set_initial_metadata()
            self.assertEqual(
                page.corpuspath.metadata.get_variable('title'),
                'PRD: Doarjja julevsámi giellaprošeavttaide')
            self.assertEqual(
                page.corpuspath.metadata.get_variable('filename'),
                'https://samediggi.no/Odasarkiiva/PRD-Doarjja-julevsami-giellaproseavttaide'
            )
            self.assertEqual(
                page.corpuspath.metadata.get_variable('mainlang'), 'sme')
            self.assertEqual(
                page.corpuspath.metadata.get_variable('genre'), 'admin')
            self.assertEqual(
                page.corpuspath.metadata.get_variable('translated_from'),
                'nob')
