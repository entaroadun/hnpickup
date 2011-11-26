#! /users/matmk2/R-2.10/bin/Rscript

## ================
## == load packages
## ================

library(rjson);

## ================
## == set up global
## == variables
## == (so I won't foget)
## == (one data point is 15 min)
## ================

TRAINING_TIMES  <<- 4:24;
TESTING_TIMES   <<- 2;
TEST_CASES      <<- 1:48;
COR_METHOD      <<- 'spearman';
FILTER_CUTOFF   <<- 0.15;

## ================
## == are there  any
## == matching time series
## == from the past that can
## == be used to predict future
## ================

run_ts_predicton_analysis <<- function ( dat, test_cases = TEST_CASES, training_times = TRAINING_TIMES, testing_times = TESTING_TIMES, cor_method = COR_METHOD, filter_cutoff = FILTER_CUTOFF, draw = FALSE ) {

  results      <- list();
  pickup_ratio <- sapply(dat[[3]][['data']],function(x){x[2]});
## ---------------------------
  for ( training_time in training_times ) {
    results[[as.character(training_time)]] <- list();
    for ( testing_time in testing_times ) {
      result <- NULL;
## - - - last X examples becomes our test set
      test_case    <- sort(length(pickup_ratio)-training_time-testing_time-test_cases+2);
## - - - we will use Y intervals to predict Z intervals
      mat_train     <- t(sapply(1:(length(pickup_ratio)-training_time-testing_time+1),function(i){pickup_ratio[i:(i+training_time-1)]}));
## - - - this matrix stores both Y and Z intervals
      mat_test      <- t(sapply(1:(length(pickup_ratio)-training_time-testing_time+1),function(i){pickup_ratio[i:(i+training_time+testing_time-1)]}));
## - - - this distance will say which past interval matches best future interval
      dis_train     <- 1-cor(t(mat_train),method=cor_method);
## - - - this will tell us how much error we've made (count only last few time slices)
      dis_test      <- 1-cor(t(mat_test[,(ncol(mat_test)-testing_time-2):ncol(mat_test)]),method=cor_method);
## - - - take most matching interval from the past
      best_guess    <- apply(dis_train[test_case,-test_case],1,which.min);
## - - - correlation looks for linear dependency, we need to find the linear factors (a and b using linear regression)
      best_guess_lm <- t(sapply(1:length(best_guess),function(i){train<-data.frame(X=mat_train[test_case[i],],Y=mat_train[best_guess[i],]);coefs<-lm(X~Y,train,weights=((1:training_time)))$coef;return(coefs);}));
      for ( i in 1:length(best_guess) ) {
	if ( draw ) {
	  print(round(c(dis_train[test_case[i],best_guess[i]],dis_test[test_case[i],best_guess[i]]),4));
	  plot(mat_test[test_case[i],],t='b',col=2,main=round(dis_train[test_case[i],best_guess[i]],3));
	  points(best_guess_lm[i,1]+mat_test[best_guess[i],]*best_guess_lm[i,2],t='b',col=3);
	  readline();
	}
	result <- rbind(result,c(dis_train[test_case[i],best_guess[i]],dis_test[test_case[i],best_guess[i]]));
      }
      print(paste('Results for',training_time,'and',testing_time,'are train',round(mean(result[,1]),3),'(',round(sd(result[,1]),3),')','test',round(mean(result[,2]),3),'(',round(sd(result[,2]),3),')','and the cor between both is',round(cor(result[,1],result[,2],method=cor_method),3)));
      results[[as.character(training_time)]][[as.character(testing_time)]] <- result;
    }
  }
## ---------------------------
  return(results);

}

