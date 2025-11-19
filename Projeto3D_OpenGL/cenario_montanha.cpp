#include <GL/glew.h>    // DEVE VIR PRIMEIRO
#include <GL/freeglut.h>
#include <GL/gl.h>
#include <GL/glu.h>

#include <cmath>
#include <iostream>
#include <vector>

#include "cenario_montanha.h"

// =========================================================================
// VARIÁVEIS 
// =========================================================================

// posição da câmera (0, 3, 15)
float cameraX = 0.0f;
float cameraY = 3.0f;
float cameraZ = 15.0f;

// angulos da camera
float horizontalAngle = 3.14f;
float verticalAngle = 0.0f;
float speed = 0.5f;

// deslocamento da camera (x, y, z)
float directionX, directionY, directionZ;
float rightVectorX, rightVectorZ;
float upVector[] = {0.0f, 1.0f, 0.0f};

// controle do tempo do frame rate
double lastTime = 0.0;
float deltaTime = 0.0f;
float waterTime = 0.0f;

// CONSTANTES do terreno
const int TERRAIN_SIZE = 100;
const float HEIGHT_SCALE = 1.0f; 
const float MAX_HEIGHT = 15.0f;
const float WATER_HEIGHT = 0.0f;

// textura splatting
const float SNOW_HEIGHT_START = 8.0f; 
const float ROCK_HEIGHT_START = 2.0f; 


void calculateDirectionVectors(){
    // calculo da direção
    directionX = cos(verticalAngle) * sin(horizontalAngle);
    directionY = sin(verticalAngle);
    directionZ = cos(verticalAngle) * cos(horizontalAngle);

    // normalização
    Vec3 dir = { directionX, directionY, directionZ };
    dir = normalize(dir);

    directionX = dir.x;
    directionY = dir.y;
    directionZ = dir.z;

    // plano de projeção xÔz 
    rightVectorX = sin(horizontalAngle - PI/2.0f);
    rightVectorZ = cos(horizontalAngle - PI/2.0f);

    // normalização
    Vec3 right = { rightVectorX, 0.0f, rightVectorZ };
    right = normalize(right);

    rightVectorX = right.x; 
    rightVectorZ = right.z;
    
}

Vec3 crossProduct(Vec3 v1, Vec3 v2) {
    Vec3 normal;
    normal.x = v1.y * v2.z - v1.z * v2.y;
    normal.y = v1.z * v2.x - v1.x * v2.z;
    normal.z = v1.x * v2.y - v1.y * v2.x;
    return normal;
}

Vec3 normalize(Vec3 v) {
    float norma = sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    if (norma == 0.0f) 
        return {0.0f, 1.0f, 0.0f}; 

    v.x /= norma;
    v.y /= norma;
    v.z /= norma;
    return v; 
}

float getTerrainHeight(float x, float z, float centerX, float centerZ, float radius) {
    float dx = x - centerX;
    float dz = z - centerZ;
    float distance = sqrtf(dx*dx + dz*dz);

    if (distance > radius) return 0.0f;

    float normalizedDist = distance / radius;
    float base = cosf(normalizedDist * PI) * 0.5f + 0.5f;
    
    const float ROUGHNESS_AMPLITUDE = 0.10f; 
    float roughness = sinf(x * 0.5f) * cosf(z * 0.5f) * ROUGHNESS_AMPLITUDE;

    roughness *= (1.0f - normalizedDist);

    float h = (base + roughness) * MAX_HEIGHT * HEIGHT_SCALE;

    if (h < 0.0f) h = 0.0f;

    return h;
}

// colorização por altura
void applyHeightColor(float height, float maxHeight) {

    if(height > SNOW_HEIGHT_START) {
        float blendFactor = (height - SNOW_HEIGHT_START) / (maxHeight - SNOW_HEIGHT_START);
        glColor3f(0.8f + 0.2f * blendFactor, 0.8f + 0.2f * blendFactor, 0.8f + 0.2f * blendFactor); 
    }
    else if (height > ROCK_HEIGHT_START) {
        float blendFactor = (height - ROCK_HEIGHT_START) / (SNOW_HEIGHT_START - ROCK_HEIGHT_START);
        glColor3f(0.3f + 0.2f * blendFactor, 0.2f + 0.2f * blendFactor, 0.1f + 0.2f * blendFactor); 
    }
    else {
        glColor3f(0.2f, 0.35f, 0.1f);
    }

}

// geração de geometria do terreno
void drawProceduralMountain(float centerX, float centerZ, float radius) {
    const float step = 1.0f;

    // Limitar loops ao retângulo 
    float startX = floorf(centerX - radius) - 1.0f;
    float endX   = ceilf(centerX + radius)  + 1.0f;
    float startZ = floorf(centerZ - radius) - 1.0f;
    float endZ   = ceilf(centerZ + radius)  + 1.0f;

    glBegin(GL_TRIANGLES);
    for (float x = startX; x < endX; x += step) {
        for (float z = startZ; z < endZ; z += step) {
            float dx = (x + 0.5f) - centerX;
            float dz = (z + 0.5f) - centerZ;
            if (sqrtf(dx*dx + dz*dz) > radius + 1.5f) continue;

            float x0 = x;
            float z0 = z;
            float x1 = x + step;
            float z1 = z + step;

            Vec3 v00 = { x0, getTerrainHeight(x0, z0, centerX, centerZ, radius), z0 };
            Vec3 v10 = { x1, getTerrainHeight(x1, z0, centerX, centerZ, radius), z0 };
            Vec3 v01 = { x0, getTerrainHeight(x0, z1, centerX, centerZ, radius), z1 };
            Vec3 v11 = { x1, getTerrainHeight(x1, z1, centerX, centerZ, radius), z1 };

            if (v00.y == 0.0f && v10.y == 0.0f && v01.y == 0.0f && v11.y == 0.0f) continue;

            // Primeiro triângulo
            Vec3 a1 = { v10.x - v00.x, v10.y - v00.y, v10.z - v00.z };
            Vec3 b1 = { v01.x - v00.x, v01.y - v00.y, v01.z - v00.z };
            Vec3 normal1 = normalize(crossProduct(a1, b1));
            glNormal3f(normal1.x, normal1.y, normal1.z);

            applyHeightColor(v00.y, MAX_HEIGHT);
            glVertex3f(v00.x, v00.y, v00.z);
            applyHeightColor(v10.y, MAX_HEIGHT);
            glVertex3f(v10.x, v10.y, v10.z);
            applyHeightColor(v01.y, MAX_HEIGHT);
            glVertex3f(v01.x, v01.y, v01.z);

            // Segundo triângulo
            Vec3 a2 = { v11.x - v10.x, v11.y - v10.y, v11.z - v10.z };
            Vec3 b2 = { v01.x - v10.x, v01.y - v10.y, v01.z - v10.z };
            Vec3 normal2 = normalize(crossProduct(a2, b2));
            glNormal3f(normal2.x, normal2.y, normal2.z);

            applyHeightColor(v10.y, MAX_HEIGHT);
            glVertex3f(v10.x, v10.y, v10.z);
            applyHeightColor(v11.y, MAX_HEIGHT);
            glVertex3f(v11.x, v11.y, v11.z);
            applyHeightColor(v01.y, MAX_HEIGHT);
            glVertex3f(v01.x, v01.y, v01.z);
        }
    }
    glEnd();
}


void drawWaterPlane(bool isReflectionPass) {
    GLfloat waterSpecular[] = {0.8f, 0.8f, 1.0f};
    GLfloat waterShininess = 60.0f;
    glMaterialfv(GL_FRONT, GL_SPECULAR, waterSpecular);
    glMaterialf(GL_FRONT, GL_SHININESS, waterShininess);

    if (isReflectionPass) {
         glColor4f(0.05f, 0.15f, 0.25f, 0.5f); 
    } else {
         glColor4f(0.1f, 0.3f, 0.5f, 0.6f); 
    }
    glBegin(GL_QUADS);
    const float size = 50.0f; 
    const float step = 1.0f; 
    const float amplitude = 0.2f; 
    const float freq = 0.8f;

    for (float i = -size / 2.0f; i < size / 2.0f; i += step) {
        for (float j = -size / 2.0f; j < size / 2.0f; j += step) {
            
            float x1 = i;
            float z1 = j;
            float x2 = i + step;
            float z2 = j + step;

            float y11 = WATER_HEIGHT + amplitude * sin(freq * (x1 + z1) + waterTime * 0.8f);
            float y12 = WATER_HEIGHT + amplitude * sin(freq * (x1 + z2) + waterTime * 0.8f);
            float y21 = WATER_HEIGHT + amplitude * sin(freq * (x2 + z1) + waterTime * 0.8f);
            float y22 = WATER_HEIGHT + amplitude * sin(freq * (x2 + z2) + waterTime * 0.8f);
            
            glNormal3f(0.0f, 1.0f, 0.0f);
            
            glVertex3f(x1, y11, z1); 
            glVertex3f(x1, y12, z2);
            glVertex3f(x2, y22, z2);
            glVertex3f(x2, y21, z1); 
        }
    }
    glEnd();


}

void renderMountains() {
    glPushMatrix();
    drawProceduralMountain(0.0f, 0.0f, 15.0f);
    glPopMatrix();


    glPushMatrix();
    drawProceduralMountain(-18.0f, -10.0f, 10.0f);
    glPopMatrix();


    glPushMatrix();
    drawProceduralMountain(25.0f, -5.0f, 20.0f);
    glPopMatrix();


    glPushMatrix();
    drawProceduralMountain(5.0f, -25.0f, 12.0f);
    glPopMatrix();


    glPushMatrix();
    drawProceduralMountain(0.0f, -50.0f, 35.0f);
    glPopMatrix();

}

void display(){
    // atualiza tempo
    double currentTime = glutGet(GLUT_ELAPSED_TIME) / 1000.0;
    deltaTime = (float)(currentTime - lastTime);
    lastTime = currentTime;
    waterTime = (float)currentTime;

    // recalcula vetores
    calculateDirectionVectors();

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // clipa geometria abaixo da água
    glEnable(GL_CLIP_PLANE0);

    const double clipOffset = 0.05;
    GLdouble clipPlane[] = { 0.0, 1.0, 0.0, - (WATER_HEIGHT + clipOffset) };
    glClipPlane(GL_CLIP_PLANE0, clipPlane);
    
    glMatrixMode(GL_MODELVIEW);
    glPushMatrix();        
        glLoadIdentity();

        glTranslatef(0.0f, 2.0f * (WATER_HEIGHT - cameraY), 0.0f);
        glScalef(1.0f, -1.0f, 1.0f);

        glCullFace(GL_FRONT);
        
        glMatrixMode(GL_MODELVIEW);
        gluLookAt(
            cameraX, cameraY, cameraZ,
            cameraX + directionX, cameraY + directionY, cameraZ + directionZ,
            upVector[0], upVector[1], upVector[2]
        );

        renderMountains();
    
        glCullFace(GL_BACK);
    glPopMatrix();

    glDisable(GL_CLIP_PLANE0);


    // visão da camera
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    gluLookAt(
        cameraX, cameraY, cameraZ,
        cameraX + directionX, cameraY + directionY, cameraZ + directionZ,
        upVector[0], upVector[1], upVector[2]
    );

    renderMountains();

    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    
    glDepthMask(GL_FALSE); 

    drawWaterPlane(false);

    glDepthMask(GL_TRUE);

    
    glutSwapBuffers();

}

void specialKeys(int key, int x, int y) {
    float rotationSpeed = 0.05f;

    
    switch(key){
        case GLUT_KEY_LEFT: 
            horizontalAngle += rotationSpeed; 
            break;
        case GLUT_KEY_RIGHT: 
            horizontalAngle -= rotationSpeed; 
            break;
        case GLUT_KEY_UP: 
            verticalAngle += rotationSpeed;
            if (verticalAngle > PI/2.0f) verticalAngle = PI/2.0f - 0.01f;
            break;
        case GLUT_KEY_DOWN: 
            verticalAngle -= rotationSpeed;
            if (verticalAngle < -PI/2.0f) verticalAngle = -PI/2.0f + 0.01f;
            break;
    }
}

void keyboard(unsigned char key, int x, int y) {
    float distance = speed * deltaTime * 50.0f; 
    switch (key) {
        case 27: exit(0); break; 
        case 'w': 
            cameraX += directionX * distance;
            cameraZ += directionZ * distance;
            break;
        case 's': 
            cameraX -= directionX * distance;
            cameraZ -= directionZ * distance;
            break;
        case 'a': 
            cameraX -= rightVectorX * distance;
            cameraZ -= rightVectorZ * distance;
            break;
        case 'd': 
            cameraX += rightVectorX * distance;
            cameraZ += rightVectorZ * distance;
            break;
    }
}

void reshape(int w, int h) {
    if (h == 0) h = 1;
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(60.0, (double)w / (double)h, 0.1, 100.0);
    glMatrixMode(GL_MODELVIEW);
}

void idle() {
    glutPostRedisplay();
}

void setupLighting() {
    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0); 
    glEnable(GL_COLOR_MATERIAL);
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE);

    GLfloat materialSpecular[] = {0.8f, 0.8f, 0.8f, 1.0f}; 
    GLfloat materialShininess = 50.0f; 
    glMaterialfv(GL_FRONT, GL_SPECULAR, materialSpecular);
    glMaterialf(GL_FRONT, GL_SHININESS, materialShininess);

    GLfloat ambientLight[] = {0.2f, 0.2f, 0.2f, 1.0f};
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLight);

    GLfloat diffuseLight[] = {1.0f, 1.0f, 1.0f, 1.0f};
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight);
    
    GLfloat specularLight[] = {1.0f, 1.0f, 1.0f, 1.0f};
    glLightfv(GL_LIGHT0, GL_SPECULAR, specularLight);
    
    GLfloat lightPosition[] = {5.0f, 10.0f, 5.0f, 0.0f}; // Luz Direcional
    glLightfv(GL_LIGHT0, GL_POSITION, lightPosition);
}

void initGL() {
    glutInitContextVersion(4, 0); 
    glutInitContextProfile(GLUT_CORE_PROFILE); 

    GLenum err = glewInit();
    if (GLEW_OK!= err) {
        std::cerr << "ERRO: Falha ao inicializar GLEW. Assegure que o pacote 'mingw-w64-x86_64-glew' esteja instalado corretamente. Erro: " << glewGetErrorString(err) << std::endl;
    } else {
        // std::cout << "SUCESSO: GLEW inicializado. Versão OpenGL: " << glGetString(GL_VERSION) << std::endl;
    }

    setupLighting();
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_BLEND); 
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(GL_CULL_FACE);
    glCullFace(GL_BACK);
    
    glClearColor(0.53f, 0.81f, 0.92f, 1.0f); 
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_ALPHA);
    glutInitWindowSize(1024, 768); 
    glutCreateWindow("Montanhas");

    glutDisplayFunc(display);
    glutReshapeFunc(reshape);
    glutIdleFunc(idle); 
    glutSpecialFunc(specialKeys); 
    glutKeyboardFunc(keyboard); 
    
    initGL();

    lastTime = glutGet(GLUT_ELAPSED_TIME) / 1000.0;
    
    glutMainLoop();
    
    return 0;
}