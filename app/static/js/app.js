
var app = angular.module('myApp', ['btford.socket-io','swipeLi','ui.bootstrap','mgcrea.ngStrap','akoenig.deckgrid','ngMaterial','ngAnimate', 'angularLazyImg'])

app.factory('socket', function (socketFactory) {
    var myIoSocket = io.connect('http://' + document.domain + ':' + location.port + "/");

    mySocket = socketFactory({
        ioSocket: myIoSocket
    });
    return mySocket;
});
app.controller('MainController', function($scope, socket) {
    $scope.comics = [],
    $scope.filtered_comics = [],
    $scope.currentPage = 1,
    $scope.numPerPage = 6;

    socket.forward('send_comics', $scope);

    $scope.$on('socket:send_comics', function (ev, data) {
        $scope.comics = data
        $scope.$watch('currentPage + numPerPage', function() {
            var begin = (($scope.currentPage - 1) * $scope.numPerPage)
            , end = begin + $scope.numPerPage;

            $scope.filtered_comics = $scope.comics.slice(begin, end);
        });
    });

    $scope.get_comics = function () {
        socket.emit('get_comics');
    };


})
