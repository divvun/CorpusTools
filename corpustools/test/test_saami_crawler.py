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
#   Copyright © 2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import print_function

import lxml.etree as etree
import sys
import requests_mock
import unittest

from corpustools import saami_crawler


#here = os.path.dirname(__file__)


class TestSamediggiNoPage(unittest.TestCase):
    def setUp(self):
        self.content = (
            '''
<!DOCTYPE html>
<html lang="en">
<head>
<style type="text/css">
.limitdisplay-user { display: none; }.limitdisplay-user-10 { display: inline; }.limitdisplay-user-block-10 { display: block; }</style>                        <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Saemiedigkie - Sametinget</title>



                <meta name="Content-Type" content="text/html; charset=utf-8" />

            <meta name="Content-language" content="sma-NO" />

                    <meta name="author" content="Making Waves" />

                <meta name="copyright" content="Sametinget" />

                <meta name="description" content="" />

                <meta name="keywords" content="Sametinget" />



    <!--[if lt IE 9 ]>
        <meta http-equiv="X-UA-Compatible" content="IE=8,chrome=1" />
    <![endif]-->

    <meta name="MSSmartTagsPreventParsing" content="TRUE" />
    <meta name="generator" content="eZ Publish" />

<link rel="Home" href="/" title="Sametinget front page" />
<link rel="Index" href="/" />
<link rel="Top"  href="/" title="Saemiedigkie - Sametinget" />
<link rel="Search" href="/content/advancedsearch" title="Search Sametinget" />
<link rel="Shortcut icon" href="/extension/sametinget/design/sametinget/images/favicon.ico" type="image/x-icon" />
<link rel="Copyright" href="/ezinfo/copyright" />
<link rel="Author" href="/ezinfo/about" />
<link rel="Alternate" type="application/rss+xml" title="RSS" href="/rss/feed/my_feed" /><link rel="Alternate" href="/layout/set/print" media="print" title="Printable version" />

    <link rel="stylesheet" type="text/css" href="/extension/sametinget/design/sametinget/stylesheets/reset.css" />
<link rel="stylesheet" type="text/css" href="/extension/ezwt/design/standard/stylesheets/websitetoolbar.css" />
<link rel="stylesheet" type="text/css" href="/design/standard/stylesheets/debug.css" />
<link rel="stylesheet" type="text/css" href="/extension/sametinget/design/sametinget/stylesheets/layout.css" />
<link rel="stylesheet" type="text/css" href="/extension/sametinget/design/sametinget/stylesheets/elements.css" />
<link rel="stylesheet" type="text/css" href="/extension/sametinget/design/sametinget/stylesheets/responsive.css" />
<link rel="stylesheet" type="text/css" href="/extension/sametinget/design/sametinget/stylesheets/plugins/accordion.css" />
<link rel="stylesheet" type="text/css" href="/extension/sametinget/design/sametinget/stylesheets/plugins/lightbox.css" />
<link rel="stylesheet" type="text/css" href="/extension/sametinget/design/sametinget/stylesheets/plugins/jquery-ui-1.8.14.custom.css" />
<link rel="stylesheet" type="text/css" href="/extension/sametinget/design/sametinget/stylesheets/plugins/bx_styles.css" />
<link rel="stylesheet" type="text/css" href="/extension/sametinget/design/sametinget/stylesheets/plugins/tools/style.css" />
<link rel="stylesheet" type="text/css" href="/extension/sametinget/design/sametinget/stylesheets/plugins/slider.css" />





<link rel="stylesheet" type="text/css" href="/extension/ezwebin/design/ezwebin/stylesheets/print.css" media="print" />
<!-- IE conditional comments; for bug fixes for different IE versions -->
<!--[if IE 5]>     <style type="text/css"> @import url(/extension/ezwebin/design/ezwebin/stylesheets/browsers/ie5.css);    </style> <![endif]-->
<!--[if lte IE 7]> <style type="text/css"> @import url(/extension/sametinget/design/sametinget/stylesheets/browsers/ie7lte.css); </style> <![endif]-->        <script type="text/javascript">

      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-29276381-1']);

      (function() {        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })();

    </script>

<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js" charset="utf-8"></script>
<script type="text/javascript" src="/extension/ezwebin/design/ezwebin/javascript/insertmedia.js" charset="utf-8"></script>
<script type="text/javascript" src="/extension/sametinget/design/sametinget/javascript/jquery-ui-1.8.4.custom.min.js" charset="utf-8"></script>
<script type="text/javascript" src="/extension/sametinget/design/sametinget/javascript/jquery.address-1.4.min.js" charset="utf-8"></script>
<script type="text/javascript" src="/extension/sametinget/design/sametinget/javascript/samediggi.js" charset="utf-8"></script>
<script type="text/javascript" src="/extension/sametinget/design/sametinget/javascript/slider.js" charset="utf-8"></script>
<script type="text/javascript" src="/extension/sametinget/design/sametinget/javascript/plugins/jquery.bxSlider.min.js" charset="utf-8"></script>
<script type="text/javascript" src="/extension/sametinget/design/sametinget/javascript/plugins/jquery.lightbox.js" charset="utf-8"></script>
<script type="text/javascript">

(function($) {
    var _rootUrl = '/', _serverUrl = _rootUrl + 'ezjscore/', _seperator = '@SEPERATOR$',
        _prefUrl = _rootUrl + 'user/preferences';

    // FIX: Ajax is broken on IE8 / IE7 on jQuery 1.4.x as it's trying to use the broken window.XMLHttpRequest object
    if ( window.XMLHttpRequest && window.ActiveXObject )
        $.ajaxSettings.xhr = function() { try { return new window.ActiveXObject('Microsoft.XMLHTTP'); } catch(e) {} };

    // (static) jQuery.ez() uses jQuery.post() (Or jQuery.get() if post paramer is false)
    //
    // @param string callArgs
    // @param object|array|string|false post Optional post values, uses get request if false or undefined
    // @param function Optional callBack
    function _ez( callArgs, post, callBack )
    {
        callArgs = callArgs.join !== undefined ? callArgs.join( _seperator ) : callArgs;
        var url = _serverUrl + 'call/';
        if ( post )
        {
            var _token = '', _tokenNode = document.getElementById('ezxform_token_js');
            if ( _tokenNode ) _token = _tokenNode.getAttribute('title');
            if ( post.join !== undefined )// support serializeArray() format
            {
                post.push( { 'name': 'ezjscServer_function_arguments', 'value': callArgs } );
                post.push( { 'name': 'ezxform_token', 'value': _token } );
            }
            else if ( typeof(post) === 'string' )// string
            {
                post += ( post ? '&' : '' ) + 'ezjscServer_function_arguments=' + callArgs + '&ezxform_token=' + _token;
            }
            else // object
            {
                post['ezjscServer_function_arguments'] = callArgs;
                post['ezxform_token'] = _token;
            }
            return $.post( url, post, callBack, 'json' );
        }
        return $.get( url + encodeURIComponent( callArgs ), {}, callBack, 'json' );
    };
    _ez.url = _serverUrl;
    _ez.root_url = _rootUrl;
    _ez.seperator = _seperator;
    $.ez = _ez;

    $.ez.setPreference = function( name, value )
    {
        var param = {'Function': 'set_and_exit', 'Key': name, 'Value': value};
            _tokenNode = document.getElementById( 'ezxform_token_js' );
        if ( _tokenNode )
            param.ezxform_token = _tokenNode.getAttribute( 'title' );

        return $.post( _prefUrl, param );
    };

    // Method version, for loading response into elements
    // NB: Does not use json (not possible with .load), so ezjscore/call will return string
    function _ezLoad( callArgs, post, selector, callBack )
    {
        callArgs = callArgs.join !== undefined ? callArgs.join( _seperator ) : callArgs;
        var url = _serverUrl + 'call/';
        if ( post )
        {
            post['ezjscServer_function_arguments'] = callArgs;
            post['ezxform_token'] = jQuery('#ezxform_token_js').attr('title');
        }
        else
            url += encodeURIComponent( callArgs );

        return this.load( url + ( selector ? ' ' + selector : '' ), post, callBack );
    };
    $.fn.ez = _ezLoad;
})(jQuery);

</script>


<script src="https://cdnjs.cloudflare.com/ajax/libs/fitvids/1.0.1/jquery.fitvids.js"></script>

<!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
<!--[if lt IE 9]>
  <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
  <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
<![endif]-->
        <script type="text/javascript">

      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-29276381-1']);

      (function() {        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })();

    </script>
</head>

<!--[if lt IE 7 ]><body class="ie6"><![endif]-->
<!--[if IE 7 ]>   <body class="ie7"><![endif]-->
<!--[if IE 8 ]>   <body class="ie8"><![endif]-->
<!--[if (gt IE 8)|!(IE)]><!--><body><!--<![endif]-->
<!-- Complete page area: START -->

<div id="fb-root"></div>
<script>(function(d, s, id) {  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/nb_NO/all.js#xfbml=1";
  fjs.parentNode.insertBefore(js, fjs);}(document, 'script', 'facebook-jssdk'));</script>


<div id="header-position">
    <div id="header">
        <div class="fontSizeBox">
            <a id="font_size_small" onclick="changeSize('fontSmall')">a</a>
            <a id="font_size_normal" onclick="changeSize('fontNormal')">a</a>
            <a id="font_size_large" onclick="changeSize('fontLarge')">a</a>
        </div>

        <div id="usermenu">

<div id="languages">
    <span id="languageSwitcher" class="sma"><span class="hidden-on-small">Åarjelsaemiengïelese</span><span class="arrowdown"></span></span>

    <ul id="languageList">
                                    <li class="nor" ><a href="/switchlanguage/to/nor">Norsk</a></li>
                                                <li class="nordsamisk" ><a href="/switchlanguage/to/nordsamisk">Davvisámegillii</a></li>
                                                                    <li class="lulesamisk" ><a href="/switchlanguage/to/lulesamisk">Julevsámegiella</a></li>
                        </ul>
</div>



    <script type="text/javascript">
    $(document).ready(function() {
        $('#languageSwitcher').toggle(function(){
            $("#languageList").show();
            $("#languages").addClass("open");
        }, function() {
            $('#languageList').hide();
            $("#languages").removeClass("open");
        });
    });
    </script>
        </div>

                    <div id="searchbox">
  <form action="/content/search">
  <div id="searchbox-inner">
    <label for="searchtext" class="hide">Search text</label>
        <input id="searchtext" name="SearchText" type="text" value="" size="12" placeholder="Search text .."/>
    <input id="searchbutton" class="button" type="submit" value="Ohtsh" title="Ohtsh" /><span class="search_btn_right"></span>
              </div>
  </form>
</div>            </div>
</div>
<!-- Change between "sidemenu"/"nosidemenu" and "extrainfo"/"noextrainfo" to switch display of side columns on or off  -->
<div id="page" class="sidemenu noextrainfo section_id_1 subtree_level_0_node_id_2">


          <!-- Top menu area: END -->
      <!-- Path area: START -->

    <!-- Path area: END -->

    <!-- Toolbar area: START -->
        <!-- Toolbar area: END -->

  <!-- Columns area: START -->
  <div id="columns" class="top-spacing ">
                            <!-- Side menu area: START -->

            <div id="leftcol" class="w240">
                        <div>
    <a href="http://www.saemiedigkie.no"><img alt="Sametinget" src="/extension/sametinget/design/sametinget/images/graphics/logo_sorSamisk.png"></a>
</div>

<div id="leftnav">

   <div class="nav-container menu-blue">
   <div class="nav-decorator decor-light blue "></div><!-- end main navsection -->
            <ul class="menu-list">

                                                    <li class="firstli"><a href="/Giele">Gïele</a>

                        </li>

                                                    <li><a href="/Lierehtimmie">Lïerehtimmie </a>

                        </li>

                                                    <li><a href="/Kultuvrejieleme">Kultuvrejieleme</a>

                        </li>

                                                    <li><a href="/Jielemh">Jielemh</a>

                        </li>

                                                    <li><a href="/Byjrese-areale-jih-kultuvrevarjelimmie">Byjrese, areale jïh kultuvrevarjelimmie</a>

                        </li>

                                                    <li><a href="/Healsoe-jih-sosijaale">Healsoe jïh sosijaale</a>

                        </li>

                                                    <li><a href="/Gaskenasjovnaale-barkoe">Gaskenasjovnaale barkoe</a>

                        </li>

                                                                                <li class="lastli"><a href="/Laante-jih-vierhtiereaktah">Laante jïh vierhtiereaktah</a>

                        </li>
                </ul>
        <div class="nav-decorator decor-heavy blue"></div><!-- end main navsection -->
           </div>
   <div class="nav-container menu-yellow">
   <div class="nav-decorator decor-light yellow "></div><!-- end main navsection -->
            <ul class="menu-list">

                                                    <li class="firstli"><a href="/Saemiedigkien-bijre">Saemiedigkien bïjre </a>

                        </li>

                                                    <li><a href="/Gaerjagaaetie">Gærjagåetie</a>

                        </li>

                                                    <li><a href="/Stipendh-jih-daaarjoeh">Stipendh jïh dåarjoeh</a>

                        </li>

                                                    <li><a href="/Biejjielaahkoe">Biejjielåhkoe</a>

                        </li>

                                                    <li><a href="/Tjaatsegh">Tjaatsegh</a>

                        </li>

                                                    <li><a href="/Preessebievnesh">Preessebïevnesh</a>

                        </li>

                                                                                <li class="lastli"><a href="/Vaaarhkoe">Våarhkoe</a>

                        </li>
                </ul>
        <div class="nav-decorator decor-heavy yellow"></div><!-- end main navsection -->
           </div></div>                 <!-- Side menu area: END -->
        </div>

    <!-- Main area: START -->


    <div id="maincol" class="w720">
        <div id="content_wrapper">


            <!-- Main area content: START -->
          <!-- Frontpage left menu set to true, hidden by js on normal screen in pagelayout.tpl -->

<div id="front_top_header">
    <div class="logo">
        <a href="/">
            <img alt="Sametinget" src="/extension/sametinget/design/sametinget/images/graphics/logo_sorSamisk.png">
        </a>
    </div>
    <div class="quote">
        <blockquote cite="http://www.saemiedigkie.no">Saemiedigkie edtja saemiej politihkeles sijjiem veaksahbåbpoe darjodh jïh saemiej iedtjh skreejredh Nöörjesne jïh sjïehteladtedh guktie saemieh maehtieh sov gïelem, sov kultuvrem jïh sov siebriedahkejieledem gorredidh jïh evtiedidh.</blockquote>
        <a href="/Saemiedigkien-bijre">Saemiedigkien bïjre </a>
    </div>
    <div class="top_links">
                    <a href="/Veeljeme-jih-veeljemelaahkoe" class="front_button">Veeljeme jïh veeljemelåhkoe</a>
                    <a href="/Stipendh-jih-daaarjoeh" class="front_button">Stipendh jïh dåarjoeh</a>
                    <a href="/Preessebievnesh/Web-tv" class="front_button">Web-tv</a>
            </div>
</div><script type="text/javascript">

    $(document).ready(function(){
        $("#slider_wrapper").sliderExtended({});
    });

</script>


<div id="slider_wrapper">`
    <ul id="slides">
                                <li data-slide="0" class="slide">
            <div class="slide_text">
                <span class="title"><small>Saernie</small>Lávdegodde- ja dievasčoahkkimat </span>

<p>Sámedikki lávdegoddečoahkkimat álget vuossárggá guovvamánu 29. b. dii 09.00 ja loahpahuvvojit maŋŋebárgga njukčamánu 1. b. dii. 15.00 rádjái. Dievasčoahkkin álgá gaskavahku guovvamánu 2. b. dii. 09.00 ja loahpahuvvo bearjadaga guovvamánu 4. b. dii. 15.00 rádjái</p><p><a href="http://www.samediggi.no/Samedikki-coahk" target="_self">Logo eambbo</a></p><p><a href="http://tv.samediggi.no/bruker/Default.aspx?live=1&amp;sid=1&amp;cid=1&amp;view=0" target="_self">Web-tv</a></p>                            </div>
            <div class="imgholder">
                <div class="divider"></div>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/media/multimedia/slideshow2/slideshow-forside/plenumsmoete/77350-1-nor-NO/Dievascoahkkin_slideshow.jpg" width="221" height="211"  alt="Lávdegodde- ja dievasčoahkkimat " title="Lávdegodde- ja dievasčoahkkimat " />



                </div>
        </li>
                                    <li data-slide="1" class="slide">
            <div class="slide_text">
                <span class="title"><small>Saernie</small><a tabindex="-1" href="/Jielemh/Duedtie/Duoji-doaibmadoarjjaortnet">Duoji doaibmadoarjjaortnet</a></span class="title">
                <p><strong>2015 duodješiehtadallamiin gaskal Sámedikki, Duojáriid Ealáhussearvvi ja Sámiid Duodji, šadde ovttamielalaččat dasa ahte árvvoštallat sáhttet go duodjeorganisašuvnnat váldit badjelasas doaibmadoarjaga hálddašeami. Sámediggi oaččui Concis Kárášjoga...</strong></p>
                <div class="links">
                    <a tabindex="-1" class="arrow" href="/Jielemh/Duedtie/Duoji-doaibmadoarjjaortnet" >Duoji doaibmadoarjjaortnet</a>
                </div>

            </div>
            <div class="imgholder">
            <div class="divider"></div>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/media/images/main-images/temabilder/soelje-c-kenneth-haetta/3591-1-nor-NO/Soelje-C-Kenneth-Haetta_slideshow.jpg" width="317" height="211"  alt="Sølje ©Kenneth Hætta" title="Sølje ©Kenneth Hætta" />



                </div>
        </li>
                                    <li data-slide="2" class="slide">
            <div class="slide_text">
                <span class="title"><small>Saernie</small><a tabindex="-1" href="/Giele/Bievnesh-saemien-gieli-bijre/Savvat-buori-sagastallama">Sávvat buori ságastallama </a></span class="title">
                <p><strong>Sámedikki presideanta Aili Keskitalo lea ilus go giellalávdegotti oasseraporta lea buktojuvvon. –Mii háliidit ahte raporta buvttihivččii buori ságastallama sámegiela boahtteáiggi hálddašeami birra, dadjá Sámedikki presideanta Aili Keskitalo.</strong></p>
                <div class="links">
                    <a tabindex="-1" class="arrow" href="/Giele/Bievnesh-saemien-gieli-bijre/Savvat-buori-sagastallama" >Sávvat buori ságastallama </a>
                </div>

            </div>
            <div class="imgholder">
            <div class="divider"></div>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/media/bilder/sametingsraadet-2013-2017/aili-keskitalo2/nrk-intervjuer-sametingspresident-aili-keskitalo-foto-jan-roger-oestby/70110-1-nor-NO/NRK-intervjuer-sametingspresident-Aili-Keskitalo-Foto-Jan-Roger-OEstby_slideshow.jpg" width="340" height="211"  alt="NRK intervjuer sametingspresident Aili Keskitalo (Foto Jan Roger Østby)" title="NRK intervjuer sametingspresident Aili Keskitalo (Foto Jan Roger Østby)" />



                </div>
        </li>
                                    <li data-slide="3" class="slide">
            <div class="slide_text">
                <span class="title"><small>Saernie</small>Dåarjoe jïh stipende Saemiedigkeste</span>

<p>Mijjieh daejtie ohtsememieride voerkelibie:</p><p><a href="/Lierehtimmie/Dotkeme-jih-jollebe-oeoehpehtimmie/Stipeanda-ja-doarjja/Stipenden-bijre-jollebe-oeoehpentaemma" target="_self">Stipende jollebe ööhpehtæmman</a> – <b>Ohtsememierie goevten 1.b.</b></p><p><a href="/Byjrese-areale-jih-kultuvrevarjelimmie/Kultuvremojhtesh/Stipeanda-ja-doarjja/Kultuvremojhtesevaarjelimmie" target="_self">Dåarjoe kultuvremojhtesevaarjelæmman</a> – <b>Ohtsememierie goevten 15.b.</b></p>                            </div>
            <div class="imgholder">
                <div class="divider"></div>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/media/multimedia/slideshow2/slideshow-forside/tilskudd-og-stipend-fra-sametinget/79822-1-nor-NO/Tilskudd-og-stipend-fra-Sametinget_slideshow.jpg" width="317" height="211"  alt="Sámediggi (Govva: Jan Helmer Olsen)" title="Sámediggi (Govva: Jan Helmer Olsen)" />



                </div>
        </li>
                                    <li data-slide="4" class="slide">
            <div class="slide_text">
                <span class="title"><small>Saernie</small><a tabindex="-1" href="/Byjrese-areale-jih-kultuvrevarjelimmie/Energije-jih-mineraalh/Samediggeraddi-ii-halit-Nussirii-doaimma">Sámediggeráđđi ii hálit Nussirii doaimma</a></span class="title">
                <p><strong>Sámediggeráđđi lea dál ovddidan ášši Sámedikki dievasčoahkkimii, dainna ávžžuhusain ahte hilgu ruvkedoaimma plánaid Nussirii ja Gumpenjunnái.</strong></p>
                <div class="links">
                    <a tabindex="-1" class="arrow" href="/Byjrese-areale-jih-kultuvrevarjelimmie/Energije-jih-mineraalh/Samediggeraddi-ii-halit-Nussirii-doaimma" >Sámediggeráđđi ii hálit Nussirii doaimma</a>
                </div>

            </div>
            <div class="imgholder">
            <div class="divider"></div>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/media/bilder/silje-karine-muotka/silje-karine-muokta_sametinget_naert/52311-1-nor-NO/Silje-Karine-Muokta_Sametinget_Naert_slideshow.jpg" width="318" height="211"  alt="Silje Karine Muokta_Sametinget_Nært" title="Silje Karine Muokta_Sametinget_Nært" />



                </div>
        </li>
                                    <li data-slide="5" class="slide">
            <div class="slide_text">
                <span class="title"><small>Saernie</small>Samarbeidserklæring med Oslo kommune</span>

<p>Sametinget og Oslo kommune signerer felles samarbeidserklæring lørdag 6. februar i Oslo.</p><p><a href="/Preessebievnesh/Pressebievnesh/PRM-Sametinget-og-Oslo-kommune-vil-styrke-samisk-spraak-og-kultur-i-Oslo" target="_self">Les mer.</a></p>                            </div>
            <div class="imgholder">
                <div class="divider"></div>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/media/multimedia/slideshow2/slideshow-forside/samarbeidserklaering-med-oslo-kommune/81598-4-nor-NO/Samarbeidserklaering-med-Oslo-kommune_slideshow.jpg" width="302" height="211"  alt="Samarbeidserklæring med Oslo kommune" title="Samarbeidserklæring med Oslo kommune" />



                </div>
        </li>
                                    <li data-slide="6" class="slide">
            <div class="slide_text">
                <span class="title"><small>Saernie</small><a tabindex="-1" href="/Byjrese-areale-jih-kultuvrevarjelimmie/Areale/Baaetieh-raeriejgujmie-baaetijen-aejkien-areale-jih-byjresepolitihkese">Buktet cealkámušaid boahtteáiggi areála ja biraspolitihkkii</a></span class="title">
                <p><strong>Saemiedigkieraerie edtja guessine mïnnedh ovmessie voenges siebriedahkine juktie raerieh åadtjodh Saemiedigkien politihkese arealen jïh byjresen sisnjeli. – Mijjieh sïjhtebe saemien tjïerth, siebrieh, jielemebarkijh jïh faagealmetjh voengesne böör...</strong></p>
                <div class="links">
                    <a tabindex="-1" class="arrow" href="/Byjrese-areale-jih-kultuvrevarjelimmie/Areale/Baaetieh-raeriejgujmie-baaetijen-aejkien-areale-jih-byjresepolitihkese" >Båetieh raeriejgujmie båetijen aejkien areale- jïh byjresepolitihkese</a>
                </div>

            </div>
            <div class="imgholder">
            <div class="divider"></div>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/media/bilder/sametingsraadet-2013-2017/thomas-aahren-og-silje-karine-muotka-foto-hanne-holmgren-lille/76967-1-nor-NO/Thomas-AAhren-og-Silje-Karine-Muotka-Foto-Hanne-Holmgren-Lille_slideshow.jpg" width="318" height="211"  alt="Thomas Åhren og Silje Karine Muotka (Foto Hanne Holmgren Lille)" title="Thomas Åhren og Silje Karine Muotka (Foto Hanne Holmgren Lille)" />



                </div>
        </li>
                </ul>
    <div class="slider_menu_wrapper">
        <ul id="slides_menu">
                            <li class="current" data-slide="0">
                    <a href="#slide0">&nbsp;</a>
                </li>
                            <li class="" data-slide="1">
                    <a href="#slide1">&nbsp;</a>
                </li>
                            <li class="" data-slide="2">
                    <a href="#slide2">&nbsp;</a>
                </li>
                            <li class="" data-slide="3">
                    <a href="#slide3">&nbsp;</a>
                </li>
                            <li class="" data-slide="4">
                    <a href="#slide4">&nbsp;</a>
                </li>
                            <li class="" data-slide="5">
                    <a href="#slide5">&nbsp;</a>
                </li>
                            <li class="" data-slide="6">
                    <a href="#slide6">&nbsp;</a>
                </li>
                    </ul>
    </div>
</div>

<div id="link_line">
    <a href="/Saemiedigkien-bijre" class="root_page">Saemiedigkien bïjre</a>
                <a href="/Saemiedigkien-bijre/Tjirkijh">Tjirkijh</a>
            <a href="/Saemiedigkien-bijre/AAaarganisasjovnestruktuvre/Stoerretjaaanghkoe">Stoerretjåanghkoe</a>
            <a href="/Saemiedigkien-bijre/AAaarganisasjovnestruktuvre/Saemiedigkieraerie">Saemiedigkieraerie</a>
            <a href="/Tjaatsegh">Tjaatsegh</a>
            <a href="/Biejjielaahkoe">Biejjielåhkoe</a>
            <a href="/Saemiedigkien-bijre/Gaskesadth-mijjine">Gaskesadth mijjine</a>

    <a href="/Saemiedigkien-bijre" class="arrow">View Saemiedigkien bïjre</a>
</div>

<div class="frontpage-categories">


        <div class="frontbox1 category">

            <div class="header w310">
                <a href="/Giele">
                    <h2>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/spraak/3927-27-sma-NO/Giele_large_square_wide.jpg" width="228" height="115"  alt="© Kenneth Hætta" title="© Kenneth Hætta" />



                            <span>Gïele</span>
                    </h2>
                </a>
            </div>
            <div class="linkliste">
                                    <a href="/Giele/Bievnesh-saemien-gieli-bijre"><h3>Bïevnesh saemien gïeli bïjre</h3></a>
                                    <a href="/Giele/Reeremedajve-saemien-gielide"><h3>Reeremedajve saemien gïelide</h3></a>
                                    <a href="/Giele/Saemien-sijjienommh"><h3>Saemien sijjienommh</h3></a>
                                <a href="/Giele" class="arrow">View Gïele</a>
            </div>





        </div>


        <div class="frontbox2 category">

            <div class="header w310">
                <a href="/Kultuvrejieleme">
                    <h2>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/kulturliv/978-6-nor-NO/Kulturliv_large_square_wide.jpg" width="228" height="115"  alt="©Kenneth Hætta" title="©Kenneth Hætta" />



                            <span>Kultuvrejieleme</span>
                    </h2>
                </a>
            </div>
            <div class="linkliste">
                                    <a href="/Kultuvrejieleme/Stipende-jih-daaarjoe"><h3>Stipende jïh dåarjoe </h3></a>
                                    <a href="/Kultuvrejieleme/Meedijah"><h3>Meedijah</h3></a>
                                    <a href="/Kultuvrejieleme/Gaarsjelimmie"><h3>Gaarsjelimmie</h3></a>
                                <a href="/Kultuvrejieleme" class="arrow">View Kultuvrejieleme</a>
            </div>





        </div>


        <div class="frontbox3 category">

            <div class="header w310">
                <a href="/Lierehtimmie">
                    <h2>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/opplaering/3915-31-sma-NO/Lierehtimmie_large_square_wide.jpg" width="228" height="115"  alt="Lïerehtimmie " title="Lïerehtimmie " />



                            <span>Lïerehtimmie </span>
                    </h2>
                </a>
            </div>
            <div class="linkliste">
                                    <a href="/Lierehtimmie/Maanagierte"><h3>Maanagïerte</h3></a>
                                    <a href="/Lierehtimmie/Maadthskuvle-jih-Jaaa"><h3>Maadthskuvle jïh Jåa</h3></a>
                                    <a href="/Lierehtimmie/Dotkeme-jih-jollebe-oeoehpehtimmie"><h3>Dotkeme jïh jollebe ööhpehtimmie</h3></a>
                                <a href="/Lierehtimmie" class="arrow">View Lïerehtimmie </a>
            </div>





        </div>


        <div class="frontbox4 category">

            <div class="header w310">
                <a href="/Jielemh">
                    <h2>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/naeringer/3891-40-sma-NO/Jielemh_large_square_wide.jpg" width="228" height="115"  alt="Foto: Aina Bye" title="Foto: Aina Bye" />



                            <span>Jielemh</span>
                    </h2>
                </a>
            </div>
            <div class="linkliste">
                                    <a href="/Jielemh/Baaatsoe"><h3>Båatsoe</h3></a>
                                    <a href="/Jielemh/Marijne-jielemh"><h3>Marijne jielemh</h3></a>
                                    <a href="/Jielemh/Jaaartaburrie"><h3>Jåartaburrie</h3></a>
                                <a href="/Jielemh" class="arrow">View Jielemh</a>
            </div>





        </div>


        <div class="frontbox1 category">

            <div class="header w310">
                <a href="/Healsoe-jih-sosijaale">
                    <h2>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/helse-og-sosial/3975-26-sma-NO/Healsoe-jih-sosijaale_large_square_wide.jpg" width="228" height="115"  alt="Healsoe jïh sosijaale" title="Healsoe jïh sosijaale" />



                            <span>Healsoe jïh sosijaale</span>
                    </h2>
                </a>
            </div>
            <div class="linkliste">
                                    <a href="/Healsoe-jih-sosijaale/Maanavaarjelimmie"><h3>Maanavaarjelimmie</h3></a>
                                    <a href="/Healsoe-jih-sosijaale/Healsoe"><h3>Healsoe</h3></a>
                                    <a href="/Healsoe-jih-sosijaale/Sosijaale"><h3>Sosijaale</h3></a>
                                <a href="/Healsoe-jih-sosijaale" class="arrow">View Healsoe jïh sosijaale</a>
            </div>





        </div>


        <div class="frontbox2 category">

            <div class="header w310">
                <a href="/Byjrese-areale-jih-kultuvrevarjelimmie">
                    <h2>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/miljoe-areal-og-kulturvern/3951-39-sma-NO/Byjrese-areale-jih-kultuvrevarjelimmie_large_square_wide.jpg" width="228" height="115"  alt="Ceavccageađgi -Transteinen (Foto: Sametinget)" title="Ceavccageađgi -Transteinen (Foto: Sametinget)" />



                            <span>Byjrese, areale jïh kultuvrevarjelimmie</span>
                    </h2>
                </a>
            </div>
            <div class="linkliste">
                                    <a href="/Byjrese-areale-jih-kultuvrevarjelimmie/Kultuvremojhtesh"><h3>Kultuvremojhtesh</h3></a>
                                    <a href="/Byjrese-areale-jih-kultuvrevarjelimmie/Eatnemegellievoete"><h3>Eatnemegellievoete</h3></a>
                                    <a href="/Byjrese-areale-jih-kultuvrevarjelimmie/Areale"><h3>Areale</h3></a>
                                <a href="/Byjrese-areale-jih-kultuvrevarjelimmie" class="arrow">View Byjrese, areale jïh kultuvrevarjelimmie</a>
            </div>





        </div>


        <div class="frontbox3 category">

            <div class="header w310">
                <a href="/Laante-jih-vierhtiereaktah">
                    <h2>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/land-og-ressursrettigheter/3963-18-sma-NO/Laante-jih-vierhtiereaktah_large_square_wide.jpg" width="228" height="104"  alt="Laante jïh vierhtiereaktah" title="Laante jïh vierhtiereaktah" />



                            <span>Laante jïh vierhtiereaktah</span>
                    </h2>
                </a>
            </div>
            <div class="linkliste">
                                    <a href="/Laante-jih-vierhtiereaktah/Laantereaktah"><h3>Laantereaktah</h3></a>
                                    <a href="/Laante-jih-vierhtiereaktah/Goeoelemereakta"><h3>Göölemereakta </h3></a>
                                    <a href="/Laante-jih-vierhtiereaktah/Goerehtalleme"><h3>Goerehtalleme</h3></a>
                                <a href="/Laante-jih-vierhtiereaktah" class="arrow">View Laante jïh vierhtiereaktah</a>
            </div>





        </div>


        <div class="frontbox4 category">

            <div class="header w310">
                <a href="/Gaskenasjovnaale-barkoe">
                    <h2>




                                                                                                                                            <img src="/var/ezwebin_site/storage/images/internasjonalt-arbeid/3939-17-sma-NO/Gaskenasjovnaale-barkoe_large_square_wide.jpg" width="228" height="115"  alt="Gaaskenaasjovnen barkoe" title="Gaaskenaasjovnen barkoe" />



                            <span>Gaskenasjovnaale barkoe</span>
                    </h2>
                </a>
            </div>
            <div class="linkliste">
                                    <a href="/Gaskenasjovnaale-barkoe/Saemien-laavenjostoe"><h3>Saemien laavenjostoe</h3></a>
                                    <a href="/Gaskenasjovnaale-barkoe/Raastendaaaresth-regijovnaale-laavenjostoe"><h3>Raastendåaresth regijovnaale laavenjostoe</h3></a>
                                    <a href="/Gaskenasjovnaale-barkoe/Gaskenasjovnaale-aalkoealmetjelaavenjostoe"><h3>Gaskenasjovnaale aalkoealmetjelaavenjostoe</h3></a>
                                <a href="/Gaskenasjovnaale-barkoe" class="arrow">View Gaskenasjovnaale barkoe</a>
            </div>





        </div>


</div>


<div class="frontpage-latest-news">
    <div class="front_library_box">
        <h2>Politihkeles siebrie</h2>
        <a class="arrow" href='Om-Sametinget/Organisasjonsstruktur/Sametingsraadet'>Saemiedigkieraerie</a><br />
        Raerie lea goh Saemiedigkien reerenasse, jïh dam biejjieladtje politihkeles barkoem reerie. Saemiedigkieraerien lïhtsegh leah nammoehtamme presidenteste, mij lea raerien åvtehke.
        <br />
        <a class="arrow" href='Om-Sametinget/Organisasjonsstruktur/Plenumsforsamlingen'>Stoerretjåanghkoe</a><br />
        Saemiedigkien stoerretjåanghkoe lea Saemiedigkien bijjemes åårgane jïh faamoe. Stoerretjåanghkoeh sïejhmemes njieljien aejkien jaepien, seamma våhkoen goh moenehtsetjåanghkoeh.
    </div>







    <div class="front-events">
                                    <h2>Mij heannede?</h2>
                                    <div class="event">
    <span>06.03.2016
     - 11.03.2016</span>
    <a href="/Biejjielaahkoe/Searva-AWG">Searvá AWG</a>
</div>                                          <div class="event">
    <span>08.03.2016
     - 08.03.2016</span>
    <a href="/Biejjielaahkoe/AAST">Generalforsamling Åarjelhsaemien Teatere</a>
</div>                                          <div class="event">
    <span>10.03.2016
     - 10.03.2016</span>
    <a href="/Biejjielaahkoe/Seminar-Joikens-frie-natur">Seminar - Joikens frie natur</a>
</div>                                              </div><div id="empty-block">
                        <div class="event">
    <span>14.03.2016
     - 17.03.2016</span>
    <a href="/Biejjielaahkoe/AIEC2016-oeoernesaavva-Guovdageaidnusne">AIEC2016 öörnesåvva Guovdageaidnusne</a>
</div>                                          <div class="event">
    <span>14.03.2016
     - 14.03.2016</span>
    <a href="/Biejjielaahkoe/Violence-Against-Indigenous-Women">Violence Against Indigenous Women </a>
</div>                                          <div class="event">
    <span>07.04.2016
     - 08.04.2016</span>
    <a href="/Biejjielaahkoe/Bovdehus-gielddaseminarii">Bovdehus gielddaseminárii</a>
</div>                  </div>

    <div class="front_library_box">
        <h2>Gærjagåetie</h2>




                                                                                                                                    <a href="/Gaerjagaaetie">        <img src="/var/ezwebin_site/storage/images/bibliotek/65917-8-sma-NO/Gaerjagaaetie_large_square_wide.jpg" width="228" height="115"  alt="Govva: Sara Marja Magga " title="Govva: Sara Marja Magga " />
        </a>



        <br/>
        <a class="arrow" href="/Gaerjagaaetie">Gærjagåetie</a>
    </div>
</div>

          <!-- Main area content: END -->

        <!-- Main area: END -->
                </div>
    </div><!-- end #columns -->

  <!-- Columns area: END -->

  <!-- Footer area: START -->


<div id="footer">
    <address>

<p>
<b>Gaahpode:</b><br />
Måanta – Bearjadahke,<br />kl. 08.00-15.30</p><p>
Telefovne: +47 78 47 40 00<br />
Telefakse: +47 78 47 40 90<br /><a href="mailto:samediggi@samediggi.no" target="_self">samediggi@samediggi.no</a></p>        </address>
    <address>

<p>
<b>Påastetjaalesijjie:</b><br />
Saemiedigkie - Sametinget<br />
Ávjovárgeaidnu 50 <br />9730 Karasjok/Kárášjohka</p><p><b><a href="/Saemiedigkien-bijre/Gaskesadth-mijjine/Bargiid-oktavuodadiedut" target="_self">Gaskesadtemebïevnesh mijjen barkijidie daesnie gaavnh.</a></b></p>    </address>
    <div class="facebook">
        <a href="http://www.facebook.com/samediggi">Saemiedigkie</a>        <p>
På Facebook kan du diskutere med oss og foreslå saker vi kan jobbe med</p>
        <div class="rss" >
            <p><a href="/rss/feed/main">Rss feed</a></p>
        </div>
    </div>
    <div class="footer_right">
        <ul>
                                        <li><a href="/Saemiedigkien-bijre/Rabas-virggit">Rabas virggit</a></li>
                            <li><a href="/Preessebievnesh">Preessebïevnesh</a></li>
                            <li><a href="/Tjaatsegh/Ohtsedh-paaastejournalesne">Ohtsedh påastejournalesne</a></li>
                            <li><a href="/Tjaatsegh">Tjaatsegh</a></li>
                            <li><a href="/Saemiedigkien-bijre/Tjirkijh/Tjirkijidie">Tjirkijidie</a></li>
                                        <a href="/user/login">Logg inn</a>

        </ul>
    </div>
</div>    <!-- Footer area: END -->

</div>
<!-- Complete page area: END --><!-- Footer script area: START -->
<!-- Footer script area: END -->




</div>

</body>
</html>
            '''
        )

    def test_url(self):
        with requests_mock.Mocker() as m:
            m.get('http://www.saemiedigkie.no', content=self.content)

            sdnp = saami_crawler.SamediggiNoPage('http://www.saemiedigkie.no')

            self.assertEqual(sdnp.url, 'http://www.saemiedigkie.no/')

    def test_parallel_links(self):
        with requests_mock.Mocker() as m:
            m.get('http://www.saemiedigkie.no', content=self.content)

            sdnp = saami_crawler.SamediggiNoPage('http://www.saemiedigkie.no')

            self.assertListEqual(sdnp.parallel_links,
                                 [sdnp.url + 'switchlanguage/to/nor',
                                  sdnp.url + 'switchlanguage/to/nordsamisk',
                                  sdnp.url + 'switchlanguage/to/lulesamisk'])

    def test_print_url(self):
        with requests_mock.Mocker() as m:
            m.get('http://www.saemiedigkie.no', content=self.content)

            sdnp = saami_crawler.SamediggiNoPage('http://www.saemiedigkie.no')

            self.assertEqual(sdnp.print_url, 'http://www.saemiedigkie.no/layout/set/print/index')

    def test_lang(self):
        with requests_mock.Mocker() as m:
            m.get('http://www.saemiedigkie.no', content=self.content)

            sdnp = saami_crawler.SamediggiNoPage('http://www.saemiedigkie.no')

            self.assertEqual(sdnp.lang, 'sma')

    def test_links(self):
        with requests_mock.Mocker() as m:
            m.get('http://www.saemiedigkie.no', content=self.content)

            sdnp = saami_crawler.SamediggiNoPage('http://www.saemiedigkie.no')

            self.assertSetEqual(
                sdnp.links,
                set([u'http://www.saemiedigkie.no/Byjrese-areale-jih-kultuvrevarjelimmie',
                     u'http://www.saemiedigkie.no',
                     u'http://www.saemiedigkie.no/Saemiedigkien-bijre/Tjirkijh/Tjirkijidie',
                     u'http://www.saemiedigkie.no/Preessebievnesh',
                     u'http://www.saemiedigkie.no/Healsoe-jih-sosijaale',
                     u'http://www.saemiedigkie.no/Gaskenasjovnaale-barkoe',
                     u'http://www.saemiedigkie.no/Healsoe-jih-sosijaale/Maanavaarjelimmie',
                     u'http://www.saemiedigkie.no/Saemiedigkien-bijre',
                     u'http://www.saemiedigkie.no/Kultuvrejieleme/Gaarsjelimmie',
                     u'http://www.saemiedigkie.no/Jielemh/Duedtie/Duoji-doaibmadoarjjaortnet',
                     u'http://www.saemiedigkie.no/Biejjielaahkoe/Searva-AWG',
                     u'http://www.saemiedigkie.no/Saemiedigkien-bijre/Gaskesadth-mijjine',
                     u'http://www.saemiedigkie.no/Saemiedigkien-bijre/AAaarganisasjovnestruktuvre/Saemiedigkieraerie',
                     u'http://www.saemiedigkie.no/Gaskenasjovnaale-barkoe/Gaskenasjovnaale-aalkoealmetjelaavenjostoe',
                     u'http://www.saemiedigkie.no/Byjrese-areale-jih-kultuvrevarjelimmie/Energije-jih-mineraalh/Samediggeraddi-ii-halit-Nussirii-doaimma',
                     u'http://www.saemiedigkie.no/Jielemh/Baaatsoe',
                     u'http://www.saemiedigkie.no/',
                     u'http://www.saemiedigkie.no/Lierehtimmie/Maanagierte',
                     u'http://www.saemiedigkie.no/Gaskenasjovnaale-barkoe/Raastendaaaresth-regijovnaale-laavenjostoe',
                     u'http://www.saemiedigkie.no/Saemiedigkien-bijre/AAaarganisasjovnestruktuvre/Stoerretjaaanghkoe',
                     u'http://www.saemiedigkie.no/Giele/Reeremedajve-saemien-gielide',
                     u'http://www.saemiedigkie.no/Healsoe-jih-sosijaale/Sosijaale',
                     u'http://www.saemiedigkie.no/Lierehtimmie/Dotkeme-jih-jollebe-oeoehpehtimmie/Stipeanda-ja-doarjja/Stipenden-bijre-jollebe-oeoehpentaemma',
                     u'http://www.saemiedigkie.no/Laante-jih-vierhtiereaktah/Laantereaktah',
                     u'http://www.saemiedigkie.no/Veeljeme-jih-veeljemelaahkoe',
                     u'http://www.saemiedigkie.no/Jielemh',
                     u'http://www.saemiedigkie.no/Jielemh/Jaaartaburrie',
                     u'http://www.saemiedigkie.no/Jielemh/Marijne-jielemh',
                     u'http://www.saemiedigkie.no/Kultuvrejieleme/Stipende-jih-daaarjoe',
                     u'http://www.saemiedigkie.no/Saemiedigkien-bijre/Gaskesadth-mijjine/Bargiid-oktavuodadiedut',
                     u'http://www.saemiedigkie.no/Gaerjagaaetie',
                     u'http://www.saemiedigkie.no/Laante-jih-vierhtiereaktah',
                     u'http://www.saemiedigkie.no/Vaaarhkoe',
                     u'http://www.saemiedigkie.no/Saemiedigkien-bijre/Rabas-virggit',
                     u'http://www.saemiedigkie.no/Gaskenasjovnaale-barkoe/Saemien-laavenjostoe',
                     u'http://www.saemiedigkie.no/Saemiedigkien-bijre/Tjirkijh',
                     u'http://www.saemiedigkie.no/Preessebievnesh/Pressebievnesh/PRM-Sametinget-og-Oslo-kommune-vil-styrke-samisk-spraak-og-kultur-i-Oslo',
                     u'http://www.saemiedigkie.no/Biejjielaahkoe/Violence-Against-Indigenous-Women',
                     u'http://www.saemiedigkie.no/Giele/Bievnesh-saemien-gieli-bijre/Savvat-buori-sagastallama',
                     u'http://www.saemiedigkie.no/Kultuvrejieleme',
                     u'http://www.saemiedigkie.no/Byjrese-areale-jih-kultuvrevarjelimmie/Eatnemegellievoete',
                     'http://www.samediggi.no/Samedikki-coahk',
                     u'http://www.saemiedigkie.no/Biejjielaahkoe/AAST',
                     u'http://www.saemiedigkie.no/Byjrese-areale-jih-kultuvrevarjelimmie/Areale/Baaetieh-raeriejgujmie-baaetijen-aejkien-areale-jih-byjresepolitihkese',
                     u'http://www.saemiedigkie.no/Stipendh-jih-daaarjoeh',
                     u'http://www.saemiedigkie.no/Giele/Bievnesh-saemien-gieli-bijre',
                     u'http://www.saemiedigkie.no/Laante-jih-vierhtiereaktah/Goerehtalleme',
                     u'http://www.saemiedigkie.no/Byjrese-areale-jih-kultuvrevarjelimmie/Areale',
                     u'http://www.saemiedigkie.no/Giele',
                     u'http://www.saemiedigkie.no/Kultuvrejieleme/Meedijah',
                     u'http://www.saemiedigkie.no/Lierehtimmie',
                     u'http://www.saemiedigkie.no/Giele/Saemien-sijjienommh',
                     u'http://www.saemiedigkie.no/Biejjielaahkoe/AIEC2016-oeoernesaavva-Guovdageaidnusne',
                     u'http://www.saemiedigkie.no/Lierehtimmie/Dotkeme-jih-jollebe-oeoehpehtimmie',
                     u'http://www.saemiedigkie.no/Biejjielaahkoe',
                     u'http://www.saemiedigkie.no/Biejjielaahkoe/Bovdehus-gielddaseminarii',
                     u'http://www.saemiedigkie.no/Biejjielaahkoe/Seminar-Joikens-frie-natur',
                     u'http://www.saemiedigkie.no/Byjrese-areale-jih-kultuvrevarjelimmie/Kultuvremojhtesh',
                     u'http://www.saemiedigkie.no/Lierehtimmie/Maadthskuvle-jih-Jaaa',
                     u'http://www.saemiedigkie.no/Laante-jih-vierhtiereaktah/Goeoelemereakta',
                     u'http://www.saemiedigkie.no/Byjrese-areale-jih-kultuvrevarjelimmie/Kultuvremojhtesh/Stipeanda-ja-doarjja/Kultuvremojhtesevaarjelimmie',
                     u'http://www.saemiedigkie.no/Healsoe-jih-sosijaale/Healsoe']))
