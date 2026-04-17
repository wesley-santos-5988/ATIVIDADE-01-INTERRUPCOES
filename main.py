; ELET0021 - Máquina de Estados
#include <xc.inc>

CONFIG  FOSC = HS, WDTE = OFF, PWRTE = OFF, BOREN = OFF, LVP = OFF, CPD = OFF, WRT = OFF, CP = OFF

#define bank0   bcf STATUS, 5
#define bank1   bsf STATUS, 5

; --- Variáveis ---
psect   udata_bank0
ESTADO: ds 1

; ==============================================================================
; VETORES ABSOLUTOS COM ORG (Livre de bugs do Linker)
; ==============================================================================
psect   vectors, class=CODE, delta=2, abs

org     0x0000
    goto    setup

org     0x0004
    bank0
    btfss   INTCON, 1       ; O botão RB0 foi apertado?
    goto    sai_int
    bcf     INTCON, 1       ; Limpa a flag de interrupção
    ; Avança o estado
    incf    ESTADO, F
    movf    ESTADO, W
    xorlw   4               ; Chegou a 4?
    btfsc   STATUS, 2       ; Se não deu Zero (Z=0), pula
    clrf    ESTADO          ; Se deu Zero (Z=1), chegou a 4. Zera o estado.
    
atualiza:
    call    tabela
    movwf   PORTD           ; Atualiza os LEDs
    
sai_int:
    retfie

; ==============================================================================
; TABELA DE ESTADOS E CÓDIGO PRINCIPAL
; ==============================================================================
psect   main_code, class=CODE, delta=2

tabela:
    movf    ESTADO, W
    xorlw   0               ; É o Estado 0?
    btfss   STATUS, 2
    goto    testa_1
    retlw   0b00000101      ; Sim! Acende RD0 e RD2

testa_1:
    movf    ESTADO, W
    xorlw   1               ; É o Estado 1?
    btfss   STATUS, 2
    goto    testa_2
    retlw   0b00000010      ; Sim! Acende RD1

testa_2:
    movf    ESTADO, W
    xorlw   2               ; Verifica se é o Estado 2
    btfss   STATUS, 2
    goto    testa_3
    retlw   0b00001100      ; Sim! Acende RD2 e RD3

testa_3:
    retlw   0b00001000      ; Se chegou aqui, é o Estado 3 (Acende RD3)  
    
setup:
    bank1
    bsf     TRISB, 0        ; RB0 como Entrada
    clrf    TRISD           ; PORTD inteira como Saída
    bsf     OPTION_REG, 6   ; Interrupção por borda de subida do clock (momento exato do aperto do botão)
    movlw   0x06	    ; Configura pinos analógicos como digitais
    movwf   ADCON1          
    
    bank0
    clrf    ESTADO          ; Inicia no Estado 0
    call    tabela          ; Pega a configuração inicial dos LEDs
    movwf   PORTD           ; Acende RD0 e RD2 imediatamente
    
    ; Configura a Interrupção Externa (INT0)
    bcf     INTCON, 1       ; Limpa flag residual
    bsf     INTCON, 4       ; Ativa o bit INTE (INT0 External Interrupt Enable)
    bsf     INTCON, 7       ; Ativa o bit GIE (Global Interrupt Enable)

loop:
    goto    loop            ; Loop infinito, esperando a interrupção acontecer