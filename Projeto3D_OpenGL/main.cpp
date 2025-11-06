#include <GL/gl.h>
#include <GL/glu.h>
#include <GL/freeglut.h>

void display() {
    // glClearColor(1,1,1,0); // define a corde fundo para branco, limpar a tela
    glClear(GL_COLOR_BUFFER_BIT); //limpa o buffer de cor
    glLoadIdentity();//limpa matriz de modelagem


    //definir os objetos
    //

    //Triangulo 2D com preenchimento vermmelho
    glColor3f(1,0,0);
    glBegin(GL_TRIANGLES);
        glVertex2f(-0.5, -0.5);
        glVertex2f(0.0, 0.5);
        glVertex2f(0.5, -0.5);
    glEnd();

    glutSwapBuffers();
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA); //modo de display
    glutInitWindowSize(640,480); //define tamanho da janela

    glutCreateWindow("Janela");

    glutDisplayFunc(display); //redesenha a tela


    glutMainLoop(); // função que inicia processamento de eventos pela GLUT 
    return 0;
}
