
var app = angular.module('myApp', ['swipeLi','ui.bootstrap','mgcrea.ngStrap','akoenig.deckgrid','ngMaterial','ngAnimate'])

app.controller('MainController', function($scope, $http, $timeout) {
    $scope.value = 1;
    $scope.job_id = ""
    $scope.now = new Date();
    var polling = function(){
        if($scope.stuff){
            return false;
        }
        var value = $http({
            method: 'GET',
            url: 'results/' + $scope.job_id
        });

        value.success(function(data, status, headers, config){
            $scope.stuff = data;
        });

        $timeout(function(){
            $scope.value++;
            polling();
        }, 1000);
    };
    polling();
});
