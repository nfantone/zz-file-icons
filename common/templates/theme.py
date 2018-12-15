import sublime

if int(sublime.version()) >= 3180:
    INDENT = " " * 8
    TEMPLATE = """{
    "rules": [

      // Sidebar Row Padding

      {
        "class": "sidebar_tree"%(row_padding)s
      },

      // Sidebar File Icons - Default

      {
        "class": "icon_file_type"%(color)s%(opacity)s%(size)s
      },

      // Sidebar File Icons - Hovered

      {
        "class": "icon_file_type"%(color_on_hover)s
        "parents": [{"class": "tree_row", "attributes": ["hover"]}]%(opacity_on_hover)s
      },

      // Sidebar File Icons - Selected

      {
        "class": "icon_file_type"%(color_on_select)s
        "parents": [{"class": "tree_row", "attributes": ["selected"]}]%(opacity_on_select)s
      }
    ]
  }
  """

else:
  INDENT = " " * 4
  TEMPLATE = """[

    // Sidebar Row Padding

    {
      "class": "sidebar_tree"%(row_padding)s
    },

    // Sidebar File Icons - Default

    {
      "class": "icon_file_type"%(color)s%(opacity)s%(size)s
    },

    // Sidebar File Icons - Hovered

    {
      "class": "icon_file_type"%(color_on_hover)s
      "parents": [{"class": "tree_row", "attributes": ["hover"]}]%(opacity_on_hover)s
    },

    // Sidebar File Icons - Selected

    {
      "class": "icon_file_type"%(color_on_select)s
      "parents": [{"class": "tree_row", "attributes": ["selected"]}]%(opacity_on_select)s
    }
  ]
  """
