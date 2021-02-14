+++
title = "Who does the best triple axel?"
date = 2021-02-14
description = "A first go at modelling some skatingscores data"
tags = ["skating"]
draft = true
+++

{{< youtube id="_WHCClGHYMw" >}}

To recap, the [first post]({{< ref "/posts/big_picture" >}}) in this series set
out the overall project: to predict grade-of-execution scores in international
singles figure skating competions, using data from the website
[skatingscores](https://skatingscores.com/). Ideally we'd like to be able to
answer high-level questions involving the relative difficulty of different
elements and the abilities of the skaters. The [second post]({{<ref
"posts/data_fetching">}}) showed how to scrape the data.

This post will start to analyse the data by fitting a relatively simple model
to a relatively homogenous subset of the data - the scores for triple axel
jumps. The triple axel seemed like a good choice for a first analysis because
it is attempted by most of the top skaters, but is difficult enough that even
the best skaters can't be 100% sure of pulling it off.

# Data

The data that we fetched in the first post come from the 2019/2020 grand prix
series, the 2020 [Four Continents
Championships](https://skatingscores.com/1920/4cc/), the 2020 European
championships and the 2020 Japanese, Russian and US national
championships. 

Of these we will look only at `3A` elements with no deductions for
under-rotation. Altogether the data records 305 qualifying triple axels,
attempted by 108 different skaters and receiving 2687 scores.

The reason for excluding jumps with a rotation deduction is that in these cases
the judges' scores are not supposed to reflect how well the jump was executed
compared to other triple axels, but to other under-rotated triple axels.

# The model

\begin{align*}
\mu &\sim N(0, 3) \\\\
ability &\sim N(0, 1) \\\\
execution &\sim N(0, \sigma_{execution}) \\\\
\eta &= \mu + ability + execution \\\\
y &\sim ordered \\, logistic(\eta, cutpoints) \\\\
cutpoints_0 &= 0 \\\\
cutpoints_{-4:+4} - cutpoints_{-5:+3} &\sim N^+(0, 0.5)
\end{align*}
