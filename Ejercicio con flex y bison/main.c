#include <gtk/gtk.h>
#include <string.h>

extern int yyparse();
extern void yyrestart(FILE *);
extern FILE *yyin;
extern int resultado;

GtkWidget *entry;
GtkWidget *label_resultado;

void calcular(GtkWidget *widget, gpointer data) {
    const char *expresion = gtk_entry_get_text(GTK_ENTRY(entry));

    // Guardar la expresión en un archivo temporal
    FILE *temp = fopen("temp_input.txt", "w");
    if (temp) {
        fprintf(temp, "%s\n", expresion);
        fclose(temp);

        // Abrir para lectura
        yyin = fopen("temp_input.txt", "r");
        if (yyin) {
            yyparse();
            fclose(yyin);

            char buffer[100];
            sprintf(buffer, "Resultado: %d", resultado);
            gtk_label_set_text(GTK_LABEL(label_resultado), buffer);
        } else {
            gtk_label_set_text(GTK_LABEL(label_resultado), "Error al leer la entrada.");
        }
    } else {
        gtk_label_set_text(GTK_LABEL(label_resultado), "Error al crear archivo temporal.");
    }
}

int main(int argc, char *argv[]) {
    gtk_init(&argc, &argv);

    GtkWidget *ventana = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(ventana), "Calculadora con Flex y Bison");
    gtk_window_set_default_size(GTK_WINDOW(ventana), 300, 150);
    gtk_container_set_border_width(GTK_CONTAINER(ventana), 10);

    GtkWidget *caja = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_add(GTK_CONTAINER(ventana), caja);

    entry = gtk_entry_new();
    gtk_box_pack_start(GTK_BOX(caja), entry, FALSE, FALSE, 0);

    GtkWidget *boton = gtk_button_new_with_label("Calcular");
    gtk_box_pack_start(GTK_BOX(caja), boton, FALSE, FALSE, 0);

    GtkWidget *boton_salir = gtk_button_new_with_label("Salir");
    gtk_box_pack_start(GTK_BOX(caja), boton_salir, FALSE, FALSE, 0);


    label_resultado = gtk_label_new("Resultado:");
    gtk_box_pack_start(GTK_BOX(caja), label_resultado, FALSE, FALSE, 0);

    g_signal_connect(boton, "clicked", G_CALLBACK(calcular), NULL);
    g_signal_connect(ventana, "destroy", G_CALLBACK(gtk_main_quit), NULL);
    g_signal_connect(boton_salir, "clicked", G_CALLBACK(gtk_main_quit), NULL);

    gtk_widget_show_all(ventana);
    gtk_main();

    return 0;
}
