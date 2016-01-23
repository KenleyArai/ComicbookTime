
var app = angular.module('myApp', ['swipeLi','ui.bootstrap','mgcrea.ngStrap'])

app.controller('MainController', function($scope, $http, $timeout) {
    $scope.value = 1;
    $scope.job_id = ""
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
        }, 5000);
    };
    polling();
});
