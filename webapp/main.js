$(function(){

  var cfg = JSON.parse($("#data").html());

  var Result = Backbone.Model.extend({

    url: function() {
      if(!this.get("complete")) {
        return cfg.results_url + this.get("exec_path")  + "/";
      } else {
        return cfg.results_url + this.get("exec_path")  + "/" + this.get("photo_name") + '.json';
      }
    },

    initialize : function(data) {
      this.set({
        photo_path : 'index_mult/' + data.exec_path + '/' + data.photo_name
      });
    },

    parse: function (data, opts) {
        if (opts.fetchType == "files") {
          return {
            "files" : data
          }
        } else if (opts.fetchType == "results") {
          return {
            res : data
          };
        } else {
          return data;
        }
    },


    defaults: function() {
      return {
        complete : false,
        error : false
      };
    }
  });

  var TodoView = Backbone.View.extend({

    //... is a list tag.
    tagName:  "li",

    // Cache the template function for a single item.
    template: _.template($('#item-template').html()),

    // The DOM events specific to an item.
    events: {
      "click .toggle"   : "toggleDone",
      "dblclick .view"  : "edit",
      "click a.destroy" : "clear",
      "keypress .edit"  : "updateOnEnter",
      "blur .edit"      : "close"
    },

    // The TodoView listens for changes to its model, re-rendering. Since there's
    // a one-to-one correspondence between a **Todo** and a **TodoView** in this
    // app, we set a direct reference on the model for convenience.
    initialize: function() {
      this.listenTo(this.model, 'change', this.render);
      this.listenTo(this.model, 'destroy', this.remove);
    },

    // Re-render the titles of the todo item.
    render: function() {
      this.$el.html(this.template(this.model.toJSON()));
      this.$el.toggleClass('done', this.model.get('done'));
      this.input = this.$('.edit');
      return this;
    },

    // Toggle the `"done"` state of the model.
    toggleDone: function() {
      this.model.toggle();
    },

    // Switch this view into `"editing"` mode, displaying the input field.
    edit: function() {
      this.$el.addClass("editing");
      this.input.focus();
    },

    // Close the `"editing"` mode, saving changes to the todo.
    close: function() {
      var value = this.input.val();
      if (!value) {
        this.clear();
      } else {
        this.model.save({title: value});
        this.$el.removeClass("editing");
      }
    },

    // If you hit `enter`, we're through editing the item.
    updateOnEnter: function(e) {
      if (e.keyCode == 13) this.close();
    },

    // Remove the item, destroy the model.
    clear: function() {
      this.model.destroy();
    }

  });


  var AppView = Backbone.View.extend({

    el: $("#evalapp"),

    events: {
      'click #upload-file-btn ' : 'uploadFile',
      'click #upload-url-btn ' : 'uploadUrl'
    },

    initialize: function() {
      this.listViews = [];
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
          self.listViews.push(new ResultView(new Result(data)));
        },
      });
    },

    uploadUrl : function() {
      var form_data = new FormData($('#url')[0]);
      var cfg = JSON.parse($("#data").html());
      var self = this;
      $.ajax({
        type: 'POST',
        url: cfg.eval_url +  '/upload_url',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: function(data) {
          self.listViews.push(new ResultView(new Result(data)));
        },
      });
    },

    render: function() {
    },
  });

  var App = new AppView;

  var ResultView = Backbone.View.extend({

    el: $("#results"),

    cfg : JSON.parse($("#data").html()),

    events: {
    },

    initialize: function(model) {
      this.model = model;
      _.bindAll(this, "render");
      this.model.bind('change:complete', this.render);
      var intervalCount = 0;
      var checkCallBack = setInterval(function(intervalModel, clearInt) {
        model.fetch({ fetchType : "files" });
        var completed = _.find(model.get("files"), function(attr) {
          return attr.name == model.get("photo_name") + ".json";
        });

        if(completed) {
          model.set("complete", true);
          model.fetch({ fetchType : "results" })
        }

        if (++intervalCount > 10 | model.get("complete")) {
          clearInterval(checkCallBack)
        }

      }, 2000, model);
      this.bind
      this.render();
    },

    render: function() {
      console.log("render")
      console.log(this.model);
      var template = _.template( $("#results-tmpl").html());
      this.$el.prepend( template(this.model.toJSON()) );
    },
  });

});
