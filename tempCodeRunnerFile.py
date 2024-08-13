if event.type == pg.MOUSEBUTTONDOWN:
            mouse_pos = pg.mouse.get_pos()
            matrix_indices = [int(mouse_pos[1]//CELL_SIZE),int(mouse_pos[0]//CELL_SIZE)]
            print(matrix_indices)
            if board[matrix_indices[0]][matrix_indices[1]] != 0:
                print(board[matrix_indices[0]][matrix_indices[1]].legal_moves(board))
    pg.display.update()
    CLOCK.tick(60)
