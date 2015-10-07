var app = angular.module('testApp', ['ngSanitize']);

app.controller('mainCtrl', ['$scope', '$http', '$sce', function($scope, $http, $sce) {
    function highlightString(string, query) {
        var re = RegExp('(' + query + ')', 'gi');

        return string.replace(re, '<em>$1</em>');
    }

    $scope.getPersons = function() {
        $scope.loading = true;
        $scope.error = null;

        var url = '/persons?page=' + encodeURIComponent($scope.params.page) +
            '&sort=' + encodeURIComponent($scope.params.sort) +
            '&order=' + encodeURIComponent($scope.params.order) +
            '&query=' + encodeURIComponent($scope.params.query); 

        $http.get(url).then(
            function(res) {
                $scope.loading = false;

                // Highlight matches if there was a search query
                if ($scope.params.query) {
                    var query = $sce.trustAsHtml($scope.params.query);
                    for (var i = res.data.persons.length - 1; i >= 0; i--) {
                        var person = res.data.persons[i];
                        person.id = highlightString(String(person.id), query);
                        person.first_name = highlightString(person.first_name, query);
                        person.last_name = highlightString(person.last_name, query);
                        person.telephone = highlightString(person.telephone, query);
                    }
                };

                $scope.persons = res.data.persons;

                var numPages = Math.ceil(res.data.totalItems / 10);
                $scope.pages = [];
                for (var i = 0; i < numPages; i++) {
                    $scope.pages.push(i + 1);
                }
            },
            function(error) {
                $scope.loading = false;
                $scope.error = 'Error retrieving the person list';
                console.log('ERROR', error);
            }
        );
    };

    $scope.search = function(query) {
        $scope.params.query = query;
        $scope.params.page = 1;
        $scope.getPersons();
    };

    $scope.sort = function(s) {
        if ($scope.params.sort === s) {
            $scope.params.order = ($scope.params.order === 'asc') ? 'desc' : 'asc';
        } else {
            $scope.params.sort = s;
            $scope.params.order = 'asc';
        }
        
        $scope.params.page = 1;

        $scope.getPersons();
    };

    $scope.setPage = function(p) {
        if (p === $scope.params.page) return;

        $scope.params.page = p;
        $scope.getPersons();
    };

    $scope.params = {
        page: 1,
        sort: 'id',
        order: 'asc',
        query: ''
    }

    $scope.getPersons();
}]);
