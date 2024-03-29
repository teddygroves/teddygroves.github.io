+++
title = "How to predict who will win Rupaul's drag race"
date = 2019-01-01
description = "Season 11 of RPDR, now with Stan!"
+++

{{< figure src="/img/emotional.png" caption="When you're about to predict the drag race" >}}

I entered [this competition](https://shiraamitchell.github.io/rpdr) to predict
the outcomes of RuPaul's Drag Race season 11 - it was really fun and I learned
a lot, so I thought I'd write down how the model I made works.

# Model
My model treats the outcomes of both Drag Race episodes and [Data For
Progress's
surveys](https://www.reddit.com/r/rupaulsdragrace/comments/bmzhfk/s11e12_rpdr_poll_did_you_rankings_get_a_makeover/)
as depending probabilistically on the abilities of the contestants. The higher
a queen's ability, the more likely it is that she will do well. Other factors -
e.g. does Ru just want to keep you around for the drama? - don't directly
feature, but can be thought of either as implicitly part of ability or as
contributing a bit of randomness.

## Priors
Although there there are at least four dimensions of drag ability, for
simplicity I assumed that these can safely be reduced to one number \(\eta_i\)
for each contestant \(i\).

I used a pretty standard multilevel structure to represent the available
pre-competition information about these ability parameters:

$$
\begin{align*}
\eta_i &\sim Normal(X_i\beta, \sigma_{\eta}) \\
\beta &\sim Normal(0,1) \\
\sigma_{\eta} &\sim halfNormal(0, 1)
\end{align*}
$$

These assumptions allow us to use some information in a design matrix $X$ to
predict how good each competitor will be, with the amounts being controlled by
the $\beta$ parameters, and deviation from the predicted ability controlled by
the parameter \(\sigma_{\eta}\).

To fill up the design matrix I used age and number of pre-competition twitter
followers. I massaged the latter numbers a little: instead of using the raw
numbers I used each contestant's rank compared to the other season
starters. This was to avoid being biased by between-season trends in the number
of followers drag race competitors tend to have.

## Episode outcomes
The trickiest bit was to connect abilities with episode outcomes, which don't
fit that neatly into a standard statistical model (at least not one that I was
aware of before working on this competiton).

Each episode ends with the remaining contestants being sorted into ordered
groups - typically these are win, high, safe, low, bottom and eliminated -
according to how well they performed. The total number of contestants changes
from week to week, and the number in each group is unpredictable - Ru often
mixes things up with double wins, double eliminations and suchlike.

To represent this structure in my model I started with the rank-ordered logit
model. This is a standard-ish model for data where some things are ranked in a
way that depends probabilistically on their latent qualities. [[http://khakieconomics.github.io/2018/12/27/Ranked-random-coefficients-logit.html][This blog]] has a
really nice explanation of the rank-ordered logit model and an interesting case
study from economics.

The main idea with a rank-logit model is that the probability that option \(i\)
comes first out of \(J\) options is

$$
\frac{\exp(\eta_i)}{\sum_{j=i}^{J}\exp(\eta_j)}
$$

The probability of a whole ranking (e.g. \(a\) beats \(b\) beats \(c\) beats
\(d\)) can be found by evaluating this equation for each number from \(1\) to
\(J-1\), then multiplying together the resulting probabilities.

This would fit the drag race if only Ru would explicitly rank every queen in
every episode, with no ties allowed. To capture what actually happens -
i.e. multiple competitors getting the same rank - the rank ordered logit model
needs to be generalised a bit.

The correct generalisation finds the probability of an outcome with ties by
enumerating all the possible no-tie orderings that are consistent with it and
averaging their probabilities. [This
paper](https://pdfs.semanticscholar.org/b6de/4079beb058979185b887fad3be0dcee8251d.pdf)
lays out the maths of this idea. I had a go at applying this approach to drag
race outcomes but didn't get very far because there are just too many no-tie
orderings to consider. Say there is one winner, two high queens, 9 safe
contestants, one low queen and two eliminees: this not-too-unusual early season
outcome has \(* 9! * 2! = 1451520\) compatible no-tie orderings.

Instead of the correct solution, I used the following approximation. For each
rank, I found the rank-logit probability that each non-eliminated queen with
that rank would came first in a contest featuring them and all the queens with
equal or worse rank. In other words, I found this number for each
non-eliminated queen:

$$
\frac{\exp(\eta_i)}{\sum_{rank(j)\geq rank(i)}^{J}\exp(\eta_j)}
$$

To find the probability of a whole episode's outcome I multiplied all of these
numbers together. 

I'm still not sure this is the best way to approximate a full rank-ordered
logit model with ties, but I was a bit encouraged when I found [[http://www.glicko.net/research/multicompetitor.pdf][this paper]] by
Mark Glickman and Jonathan Hennessy. The authors use the same approximation
with some success to model competitive downhill skiing, which it turns out is
structurally kind of similar to the drag race! They also explain the model very
nicely - check it out!

## Viewer survey data
Even if the model extracted as much information as possible from the outcome
data, there would still be some room for improvement, as the final result
doesn't always tell the whole story. Some wins are more impressive than others,
and sometimes even a winning performance can reveal long-term limitations. To
try and capture this kind of dynamic I thought the survey results on data for
progress's spreadsheet might be a nice complement to the outcome data. Whereas
the outcomes are nice because they are the exact same thing the model wants to
predict, the survey responses are also nice because they use extra information
that isn't available in the outcomes.

The survey data consists of binary choices between two current contestants -
the answerer has to enter a winner and a loser, and the time they took to make
the choice is recorded. I decided to only use data from the most recent
available survey out of fear that old ones might mess things up. I found the
aggregate win/loss score for each pair and modelled these as depending on the
same abilities as the episode outcome data, according to the following
equation:

$$
wins_{ij} \sim Binomial(comparisons_{ij}, logit^{-1}(\eta_i -\eta_j))
$$

Putting the same \eta variables in two different likelihood functions is a
really simple example of joint modelling, which you can find out more about in
[[https://www.sambrilleman.com/talk/2018_contributed_stancon/][this video]].

# Implementation
I largely followed [Shira Mitchell's
approach](https://shiraamitchell.github.io/rpdr#model] to representing drag
race outcomes in Stan - the ability parameters for the contestants in each
episode are sorted according to the outcome, making it much easier to calculate
all the (log scale) probabilities. Here's how I implemented the custom
likelihood function described above:

``` stan
functions {
  real rpdr_outcome_lp(vector ability, int[] episode_rank){
    real out = 0;
    int first_in_group = 1;
    for (contestant in 1:rows(ability)){
      if ((contestant > 1)
          && (episode_rank[contestant] > episode_rank[contestant-1])){
        first_in_group = contestant;
      }
      if (episode_rank[contestant] < max(episode_rank)){
        out += ability[contestant] - log_sum_exp(ability[first_in_group:]);
      }
  }
  return out;
  }
}
```

Here's the rest of the model:

```stan
data {
  int<lower=1> N;         // Number of episode participations
  int<lower=1> K;         // Number of predictors
  int<lower=1> E;         // Number of episodes
  int<lower=1> C;         // Number of contestants
  int<lower=1> N_survey;  // Number of surveys
  matrix[C, K] X;         // Contestant level predictors
  // episode data
  int<lower=1> N_episode_contestant[E];
  int<lower=1,upper=6> episode_rank[N];
  int<lower=1,upper=C> contestant[N];
  // survey data
  int<lower=1,upper=C> survey_contestant[N_survey];
  int<lower=1,upper=C> survey_opponent[N_survey];
  int<lower=1> survey_count[N_survey];
  int<lower=0> survey_wins[N_survey];
  // config 
  int<lower=0,upper=1> use_survey;
  int<lower=0,upper=1> use_episodes;
}
parameters {
  vector[C] ability_z;
  real<lower=0> sigma_ability;
  vector[K] beta;
}
transformed parameters {
  vector[C] ability = X * beta + ability_z * sigma_ability;
}
model {
  int pos = 1;
  // priors
  ability_z ~ normal(0, 1);
  beta ~ normal(0, 1);
  sigma_ability ~ normal(0, 1);
  // likelihood
  if (use_survey == 1){
    survey_wins ~ binomial_logit(survey_count, ability[survey_contestant] - ability[survey_opponent]);
  }
  if (use_episodes == 1){
    for (e in 1:E){
      int contestants[N_episode_contestant[e]] = segment(contestant, pos, N_episode_contestant[e]);
      int episode_ranks[N_episode_contestant[e]] = segment(episode_rank, pos, N_episode_contestant[e]);
      target += rpdr_outcome_lp(ability[contestants], episode_ranks);
      pos += N_episode_contestant[e];
    }
  }
}
```
I used [pandas](https://pandas.pydata.org/),
[pystan](https://pystan.readthedocs.io/en/latest/) and
[arviz](https://arviz-devs.github.io/arviz/) to get data in and out of the
resulting model. [Here](https://github.com/teddygroves/drag_race)'s a link to a
github repository with all the code.

# Results

Here's what the model thinks of the remaining season 11 competitors (the low
and high are the 10% and 90% quantiles of the posterior distributions). I
didn't include survey data this week as it was a bit out of date.

``` shell
                          ability_low  ability_median  ability_high
contestant_name                                                    
Brooke Lynn Hytes               -0.04            0.22          0.59
Yvie Oddly                      -0.12            0.13          0.48
Silky Nutmeg Ganache            -0.12            0.12          0.44
A'keria Chanel Davenport        -0.11            0.11          0.42
Vanessa Vanjie Mateo            -0.17            0.09          0.35
```

These results more or less agree with my take on the current situation. Brooke
is the clear frontrunner, with very little to choose between the remaining four
and Vanjie probably the weakest.

I've also been sanity checking the model by looking at who it thinks were the
best RPDR contestants of all time. This is a bit tricky as there aren't any
between-season comparisons.

``` shell
                    ability_low  ability_median  ability_high
contestant_name                                              
Sasha Velour              -0.00            0.28          0.65
Jinkx Monsoon             -0.01            0.27          0.65
Tyra Sanchez              -0.01            0.27          0.66
Bianca Del Rio            -0.05            0.26          0.67
Sharon Needles            -0.05            0.24          0.63
Brooke Lynn Hytes         -0.04            0.22          0.59
Ginger Minj               -0.04            0.21          0.53
Shea Couleé               -0.05            0.21          0.54
Violet Chachki            -0.07            0.19          0.53
Manila Luzon              -0.05            0.18          0.52
Raja                      -0.07            0.18          0.53
Bob the Drag Queen        -0.07            0.18          0.51
Aquaria                   -0.08            0.17          0.50
Roxxxy Andrews            -0.08            0.17          0.49
Alaska                    -0.08            0.15          0.47
Chad Michaels             -0.13            0.14          0.51
Kim Chi                   -0.12            0.13          0.47
Yvie Oddly                -0.12            0.13          0.48
Nina Flowers              -0.12            0.13          0.51
Trinity Taylor            -0.11            0.13          0.44
```

This seems more or less plausible - as Yvie Oddly observed this season, Sasha
Velour had talent!

{{< figure caption="When your predictions recognise that your fave is the best"
src="/img/emotional_rose.png" >}}

# Things that could be improved
This was a really fun task - I learned lots about ordinal models and came up
with something that more or less passed my smell test. There are a few extra
features it would be nice to add - I'm not sure I'll ever get round to them but
it's still a good exercise.

## Probabilistic predictions
Rather than just ranking competitors by ability it would be nice if the model
outputted the probability of each queen winning or being eliminated in each
episode. This wasn't strictly required for this competition as only a discrete
best/worst prediction for the next episode was needed, but would make it a lot
easier to test the model. Unfortunately a custom random number generating Stan
function would be needed for this and I didn't quite have the emotional energy
to attempt to implement one.

## Extra ability dimensions
There were a few times when I thought the model was a bit limited by only
having one ability dimensions. For example, in the snatch game episode I
thought it was pretty clear that personality queens Nina West and Silky Nutmeg
Ganashe would do better than indicated by their overall track records.

## Separate lipsync mechanics
I think it would be nice to handle lipsyncs with a separate model. I initially
took this approach but gave up as I seemed to be doing everything twice and the
lipsync component of the model wasn't having a very big effect. Of course, as
soon as I did this Rajah emerged as season 11's lipsync assassin and I started
getting second thoughts.

