(setq org-publish-project-alist
      '(("teddys_picnic" :components ("base" "posts"))
        ("base"
         :base-directory "/Users/tedgro/Code/teddys_picnic/"
         :base-extension "org"
         :publishing-directory "/Users/tedgro/Code/teddys_picnic/"
         :recursive nil
         :publishing-function org-html-publish-to-html
         :headline-levels 4
         :table-of-contents nil
         :with-author nil
         :html-head "<link rel='stylesheet' href='css/gongzhitaao.css' type='text/css'/>"
         :auto-preamble nil
         :html-preamble-format (("en"
                                 "<div class='main-header'><h1><a href='./index.html'> Teddy's Picnic </a></h1></div>"))
         :html-postamble nil
         :section-numbers nil
         )

        ("posts"
         :base-directory "/Users/tedgro/Code/teddys_picnic/posts/"
         :base-extension "org"
         :publishing-directory "/Users/tedgro/Code/teddys_picnic/posts/"
         :recursive t
         :publishing-function org-html-publish-to-html
         :headline-levels 4
         :table-of-contents nil
         :with-author nil
         :html-head "<link rel='stylesheet' href='../css/gongzhitaao.css' type='text/css'/>"
         :auto-sitemap t
         :sitemap-filename "sitemap.org"
         :sitemap-title ""
         :sitemap-sort-files anti-chronologically
         :auto-preamble nil
         :html-preamble-format (("en"
                                 "<div class='main-header'><h1><a href='../index.html'> Teddy's Picnic </a></h1></div>"))
         :section-numbers nil
         :html-postamble nil)))
