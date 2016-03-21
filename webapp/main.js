$(function(){

  var cfg = JSON.parse($("#data").html());

  var Message = Backbone.Model.extend({

    initialize : function(message) {
      this.set({
        "message"  : message
      });
    },

    defaults: function() {
      return {
        "message" : ""
      };
    }
  });

  var Result = Backbone.Model.extend({
    //
    // url: function() {
    //   if(!this.get("complete")) {
    //     return cfg.results_url + this.get("exec_path")  + "/";
    //   } else {
    //     return cfg.results_url + this.get("exec_path")  + "/" + this.get("photo_name") + '.sift.json';
    //   }
    // },
    parse: function (data, opts) {
      if (opts.fetchType == "files") {
        return {
          "files" : data
        }
      } else if (opts.fetchType == "results") {
        resAttr = this.get('res') || {};
        resAttr[opts.attrName] = data;
        return {
          res : resAttr
        };
      } else if (opts.fetchType == "raw") {

        photo_name = _.find(data, function(elem) {
          ext = elem.name.split('.').pop();
          return _.contains(['JPG','jpg','png','PNG'], ext);
        });

        res_files = _.filter(data, function(elem) {
          ext = elem.name.split('.').pop();
          return _.contains(['json'], ext);
        });

        if(!photo_name) {
          return  {
            valid : false
          }
        }

        return {
          valid : true,
          complete : false,
          files : data,
          resFiles : res_files,
          photo_name : photo_name.name,
          photo_path : 'index_mult/' + this.get('exec_path') + '/' + photo_name.name
        }
      } else {
        return data;
      }
    },

    sync : function(method,model,xhr) {
      Backbone.sync(method,model,xhr)
    },

    defaults: function() {
      return {
        complete : false,
        error : false,
        valid : true
      };
    },

    toHighCharts : function(sortedBy) {
      if(typeof this.get('res') !== 'undefined') {

        sortBy = sortedBy || "sift";
        var series = [];
        if(typeof this.get('res')[sortedBy] === 'undefined') {
          sortedBy = _.keys(this.get('res'))[0];
        }

        XAxis = [];
        values = [];

        sorted = _.chain(_.map(this.get("res")[sortedBy], function(attr, key) {
          return {
            value : parseFloat(attr.map),
            name : key
          }
        })).sortBy('value').each(function(attr) {
          XAxis.unshift(attr.name);
          values.unshift(attr.value);
        });

        series.push({
            name : sortedBy,
            data : values
        })


        _.each(this.get('res'), function(elem, key) {
          if(key == sortedBy) return ;
          serie = [];
          _.each(XAxis, function(cpt) {
            serie.push(parseFloat(elem[cpt].map))
          })
          series.push({
            name : key,
            data : serie
          });
        });

        console.log(series)
        return {
          chart: {
            type: 'bar',
            height: 1000,
          },
          title : { text : this.get('photo_name') },
          subtitle :  { text : this.get("hello") },
          xAxis : {
            categories : XAxis
          },
          yAxis: {
            min: 0,
            title: {
              text: '%',
              align: 'high'
            },
            labels: {
              overflow: 'justify'
            },
            tooltip: {
              valueSuffix: '%'
            },
          },
          plotOptions: {
            bar: {
              dataLabels: {
                enabled: true
              }
            }
          },
          legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            x: -40,
            y: 80,
            floating: true,
            borderWidth: 3,
            groupPadding:0.1,
              pointWidth:20,
            backgroundColor: ((Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'),
            shadow: true
          },
          credits: {
            enabled: false
          },
          series : series
        };
      } else return {};
    },

    initialize : function(data) {
      if(!data.exec_path) {
        this.set({
          valid : true,
          exec_path : data.name,
          photo_path : "",
          photo_name : "",
          concepts : []
        });
      } else {
        this.set({
          photo_path : 'index_mult/' + data.exec_path + '/' + data.photo_name,
          concepts : [],
          valid : true
        });
      }
    }
  });

  var Results = Backbone.Collection.extend({
    model: Result,
    url: '/index_mult/',

    initialize : function(a,b,c) {
      this.urls = [];
    },

    parse : function(data, opts) {
      return data;
    },

    paginate : function(page, size) {
      var self = this;
      models =  this.models.slice(page * size ,(page * size) + size);
      _.each(models, function(model) {
        model.fetch({
          fetchType : "raw",
          url : "index_mult/" + model.get('exec_path'),
          success : function(model) {
            if(!model.get('valid')) {
              self.remove(model);
              models.remove(model)
              return;
            }
          }
        });
      });
      return models;
    },

    addOne : function(model, collection) {
      var self = this;

    }
  });


  var AppView = Backbone.View.extend({

    el: $("#evalapp"),

    tagName:  "div",

    events: {
      'click #upload-file-btn ' : 'uploadFile',
      'click #upload-url-btn ' : 'uploadUrl'
    },

    initialize: function(data,b,c) {
      console.log(data,b,c)
      var self = this;
      this.currentPage = 0;
      this.listViews = [];
      this.collection = new Results();
      this.collection.fetch({
        remove: false,
        success : this.paginate.bind(this)
      });

      $(window).scroll(function() {
        if($(window).scrollTop() + $(window).height() >  $(document).height() - 10) {
          self.paginate();
        }
      });
    },


    uploadFile : function() {
      var form_data = new FormData($('#upload-file')[0]);
      var self = this;
      $.ajax({
        type: 'POST',
        url: cfg.eval_url + '/upload',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: function(data) {
          var view = new ResultView(new Result(data))
          $("#results").prepend(view.render().el);
          self.listViews.push(view);
        },
        error: function(err) {
          var view = new AlertView(new Message(err.responseText))
          $("#alerts").prepend(view.render().el);
        }
      });
    },

    uploadUrl : function() {
      var cfg = JSON.parse($("#data").html());
      var url =  $('#input-url').val();
      var self = this;
      $.ajax({
        type: 'POST',
        url: cfg.eval_url +  '/upload_url',
        data: JSON.stringify({ url : url }),
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: function(data) {
          var view = new ResultView(new Result(data))
          $("#results").prepend(view.render().el);
          self.listViews.push(view);
        },
        error : function(err) {
          var view = new AlertView(new Message(err.responseText))
          $("#alerts").prepend(view.render().el);
        }
      });
    },

    paginate : function() {
      var self = this;
      _.each(this.collection.paginate(this.currentPage, 1), function(model) {
        if(model.get("valid")) {
          var view = new ResultView(model);
          $("#results").append(view.render().el);
          self.listViews.push(view);
        } else {
          console.log("not valid")
        }
      });
      this.currentPage++;
    },


    render: function() {
    },
  });

  var App = new AppView;

  var ResultView = Backbone.View.extend({

    tagName : "div",

    cfg : JSON.parse($("#data").html()),

    events: {
    },

    initialize: function(model) {
      this.model = model;
      _.bindAll(this, "render");
      this.resBinding = [];
      this.model.on('resUpdated', this.render);
      this.model.bind('change:concepts', this.render);

      var intervalCount = 0;
      var checkCallBack = setInterval(function(intervalModel, clearInt) {

        model.fetch({ fetchType : "files" });
        var resFiles = _.filter(model.get("files"), function(attr) {
          return attr.name.endsWith(".json");
        });

        _.each(resFiles, function(file) {
            tokenizedFile = file.name.split('.')
            tokenizedFile.pop()
            resName = tokenizedFile.pop()// getting the sift or color extension
            model.set('complete', true);
            model.fetch({
              fetchType : "results",
              attrName : resName,
              url : "index_mult/" + model.get("exec_path") + "/" + file.name,
              success : function(model){
                console.log(model)
                model.trigger("resUpdated");
              }
            });
        });

        if ((model.get("res") && (model.get("res").sift && model.get("res").color))) {
          clearInterval(checkCallBack)
        }

        if (++intervalCount > 100) {
          clearInterval(checkCallBack)
        }

      }, 2000, model);
    },

    render: function() {
      var template = _.template( $("#results-tmpl").html());
      this.$el.html(template(this.model.toJSON()));
      if(this.model.get("res") && (this.model.get('res')['sift'] || this.model.get('res')['color'])) {
        var concepts = _.filter(this.model.get('res').sift, function(elem) {
          return elem.is_concept === "1";
        });
        this.model.set("concepts", concepts);
        this.$(".barchart").highcharts(this.model.toHighCharts('sift'));
      }
      return this;
    },
  });


  var AlertView = Backbone.View.extend({

    tagName : "div",

    events: {
    },

    destroy_view: function() {

      // COMPLETELY UNBIND THE VIEW
      this.undelegateEvents();

      this.$el.removeData().unbind();

      // Remove view from DOM
      this.remove();
      Backbone.View.prototype.remove.call(this);

    },

    initialize: function(model) {
      this.model = model;
      setTimeout(this.destroy_view.bind(this), 10000);
    },

    render: function() {
      var template = _.template( $("#alert-tmpl").html());
      this.$el.html(template(this.model.toJSON()));
      return this;
    },
  });

});
