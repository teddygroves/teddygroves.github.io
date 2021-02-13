+++
title = "Data Analysis on Ice"
summary = "Some posts about ice skating"
date = 2021-01-01
+++

![](/img/yoi_intro.png)

In the locked down midwinter I was introduced to [Yuri!!! on
Ice](https://myanimelist.net/anime/32995/Yuri_on_Ice), at which point it was
only a matter of time before a statistical analysis of international figure
skating data appeared here.

It turns out that figure skating is very statistically interesting, especially
since some recent rule changes. To make matters even better, the format fits
quite closely with my experience of analysing football players, and there is a
fantastic online resource called [skatingscores](https://skatingscores.com/)
where you can easily find all the data you need.

My aim with this series of posts is to illustrate all aspects of the kind of
data analysis workflow that I like, from getting an idea in the first place, to
fetching some data, putting it in a convenient format, modelling it, analysing
and visualising the results and then drawing some interesting
conclusions. Ideally the steps will roughly agree with [this paper about
Bayesian workflow](https://arxiv.org/abs/2011.01808).

The overall idea might be familiar if you've seen the amazing website [FC
Python](https://fcpython.com/). What you find here will likely be a bit more
focused on my preoccupations (so figure skating, Stan, the pandas [transform
method](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.core.groupby.DataFrameGroupBy.transform.html),
maybe a little bit of philosophy).

You can find all the code I use
[here](https://github.com/teddygroves/figure_skating), and here are all the
posts:

{{< skating_posts >}}

