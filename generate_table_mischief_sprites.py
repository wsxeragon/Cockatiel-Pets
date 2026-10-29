import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Set paths
base_dir = os.path.dirname(os.path.abspath(__file__))
scratch_dir = os.path.join(r'C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae', 'scratch')
if scratch_dir not in sys.path:
    sys.path.append(scratch_dir)

from table_mischief_animator import create_table_mischief_animator

def generate_table_mischief_sprites(crest_type="classic", num_frames=400, scale=2.0):
    """
    Renders num_frames (400 frames, 25 FPS, 40ms/frame) transparent PNG frames
    for TABLE_MISCHIEF behavior into assets/sprites_<crest_type>/.
    """
    out_dir = os.path.join(base_dir, "assets", f"sprites_{crest_type}")
    os.makedirs(out_dir, exist_ok=True)
    
    anim = create_table_mischief_animator(crest_type=crest_type)
    sprites_l = anim['sprites_left']
    sprites_r = anim['sprites_right']
    draw_mug = anim['draw_mug']
    draw_bell = anim['draw_bell']
    draw_pencil = anim['draw_pencil']
    draw_table = anim['draw_table']

    canvas_w, canvas_h = 320, 200
    table_top_y = 105
    bird_base_y = table_top_y - 74 # 31
    S = scale
    total_frames = int(200 * S) # 400
    
    font_msyh = "C:/Windows/Fonts/msyh.ttc"
    font_fx = ImageFont.truetype(font_msyh, 14) if os.path.exists(font_msyh) else None
    font_bold = ImageFont.truetype(font_msyh, 16) if os.path.exists(font_msyh) else None

    # Pre-calculate physics states
    pencil_states = []
    bell_states = []
    mug_states = []
    
    # 1. Pencil
    p_x, p_y, p_ang = 230.0, 102.0, 0.0
    p_vx, p_vy = 0.0, 0.0
    for f in range(total_frames):
        orig_f = f / S
        if orig_f < 45:
            pass
        elif 45 <= orig_f < 52:
            dt = orig_f - 45
            p_x = 230.0 + dt * 1.5
            p_ang = (p_x - 230.0) * 8.0
        elif 52 <= orig_f < 56:
            dt = orig_f - 52
            p_x = 240.5 + dt * 6.5
            p_ang = (p_x - 230.0) * 10.0
        elif orig_f >= 56:
            if f == int(56 * S):
                p_x, p_y = 265.0, 102.0
                p_vx, p_vy = 2.2 / S, -0.6 / S
            p_vy += 0.75 / (S * S)
            p_x += p_vx
            p_y += p_vy
            p_ang += 22.0 / S
            if p_y >= 173.0:
                p_y = 173.0
                if abs(p_vy) > 1.0 / S:
                    p_vy = -p_vy * 0.40
                    p_vx *= 0.65
                else:
                    p_vy = 0.0
                    p_vx = 0.0
                    p_ang = round(p_ang / 180.0) * 180.0
        pencil_states.append((p_x, p_y, p_ang))

    # 2. Bell
    b_x, b_y, b_ang = 155.0, 96.0, 0.0
    b_vx, b_vy = 0.0, 0.0
    for f in range(total_frames):
        orig_f = f / S
        if orig_f < 87:
            pass
        elif 87 <= orig_f < 93:
            sub = orig_f - 87
            b_x = 155.0 - (sub ** 1.6) * 7.5
            b_ang = -(155.0 - b_x) * 12.0
        elif orig_f >= 93:
            if f == int(93 * S):
                b_x, b_y = 48.0, 96.0
                b_vx, b_vy = -2.4 / S, -0.8 / S
            b_vy += 0.70 / (S * S)
            b_x += b_vx
            b_y += b_vy
            b_ang -= 25.0 / S
            if b_y >= 169.0:
                b_y = 169.0
                if abs(b_vy) > 1.2 / S:
                    b_vy = -b_vy * 0.50
                    b_vx *= 0.6
                else:
                    b_vy = 0.0
                    b_vx = 0.0
        bell_states.append((b_x, b_y, b_ang))

    # 3. Mug
    m_x, m_y, m_ang = 75.0, 93.0, 0.0
    m_vx, m_vy = 0.0, 0.0
    for f in range(total_frames):
        orig_f = f / S
        if orig_f < 120:
            pass
        elif 120 <= orig_f < 134:
            sub = orig_f - 120
            m_x = 75.0 - sub * (33.0 / 14.0)
        elif 134 <= orig_f < 138:
            sub = orig_f - 134
            m_x = 42.0 - sub * 0.8
            m_ang = -sub * 16.0
        elif orig_f >= 138:
            if f == int(138 * S):
                m_x, m_y = 38.8, 94.0
                m_vx, m_vy = -1.2 / S, 0.4 / S
                m_ang = -64.0
            m_vy += 0.80 / (S * S)
            m_x += m_vx
            m_y += m_vy
            m_ang -= 18.0 / S
            if m_y >= 166.0:
                m_y = 166.0
                m_vx = 0.0
                m_vy = 0.0
                m_ang = -90.0
        mug_states.append((m_x, m_y, m_ang))

    print(f"Generating {total_frames} transparent frames for {crest_type} in {out_dir}...")
    
    for f in range(total_frames):
        orig_f = f / S
        
        # Relative motion offset for table and fallen objects at takeoff: uniform linear slide-out (no acceleration)
        table_ox = 0.0
        table_oy = 0.0
        if orig_f >= 178:
            exit_t = (orig_f - 178) / 21.0
            table_ox = - exit_t * 360.0 # 匀速直线滑出，不加速
            table_oy = 0.0
            
        frame_img = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
        d = ImageDraw.Draw(frame_img)
        
        # 1. Draw Table and floor with relative offset
        draw_table(frame_img, ox=table_ox, oy=table_oy, alpha=1.0, is_transparent=True)
        
        # Draw Props with relative offset
        mx, my, mang = mug_states[f]
        draw_mug(frame_img, mx + table_ox, my + table_oy, mang, alpha=1.0)
        
        bx, by, bang = bell_states[f]
        draw_bell(frame_img, bx + table_ox, by + table_oy, bang, alpha=1.0)
        
        px, py, pang = pencil_states[f]
        draw_pencil(frame_img, px + table_ox, py + table_oy, pang, alpha=1.0)
        
        # Visual FX
        if 52 <= orig_f <= 56:
            d.line([(242, 98), (248, 94)], fill='#e2e8f0', width=2)
            d.line([(242, 106), (248, 110)], fill='#e2e8f0', width=2)
        if 67 <= orig_f <= 72:
            d.ellipse([(276, 172), (288, 176)], fill=(203, 213, 225, 180))
            
        if 88 <= orig_f <= 94:
            sub = orig_f - 88
            note_x = int(148 - sub * 3)
            note_y = int(80 - sub * 3)
            d.text((note_x, note_y), "♫", fill='#f59e0b', font=font_fx)
        if 103 <= orig_f <= 108:
            d.arc([(10, 160), (32, 176)], 180, 360, fill='#d97706', width=1)
            d.text((15, 150), "✦", fill='#f59e0b', font=font_fx)

        # Mug floor crash & persistent coffee puddle
        if orig_f >= 146:
            sub = orig_f - 146
            spread = min(1.0, 0.65 + sub * 0.08)
            pw = int(16 * spread)
            cx, cy = int(28 + table_ox), int(177 + table_oy)
            d.ellipse([(cx - pw, cy - 3), (cx + pw, cy + 3)], fill=(92, 45, 22, 220))
            d.ellipse([(cx - int(pw * 0.7), cy - 2), (cx + int(pw * 0.7), cy + 1)], fill=(120, 60, 30, 180))
            d.ellipse([(cx - pw - 4, cy), (cx - pw - 1, cy + 2)], fill=(92, 45, 22, 200))
            d.ellipse([(cx + pw + 2, cy - 1), (cx + pw + 5, cy + 1)], fill=(92, 45, 22, 200))
            d.ellipse([(cx + 3, cy - 5), (cx + 6, cy - 3)], fill=(92, 45, 22, 180))
            
            if sub <= 5:
                d.text((24, 148), "💥", fill='#ef4444', font=font_bold)
                d.text((42, 155), "✦", fill='#f59e0b', font=font_fx)
                d.text((10, 160), "✦", fill='#f59e0b', font=font_fx)
                
        if 166 <= orig_f <= 176:
            sub = orig_f - 166
            d.text((int(105 - sub), int(15 - sub * 2)), "♪", fill='#ec4899', font=font_fx)
            d.text((int(135 + sub), int(10 - sub * 2)), "♫", fill='#8b5cf6', font=font_fx)
            d.text((120, int(5 - sub * 2)), "♬", fill='#06b6d4', font=font_fx)

        if 178 <= orig_f <= 188:
            dust_t = (orig_f - 178) / 10.0
            alpha_dust = int(180 * (1.0 - dust_t))
            for lx in [62 + 12 + table_ox, 242 + 12 + table_ox]:
                d.line([(lx, 175), (lx + 14, 175)], fill=(148, 163, 184, alpha_dust), width=1)

        # 2. Determine Bird Pose & Position
        bird_x = 170.0
        bird_y = bird_base_y
        bird_sprite_name = 'idle_0'
        facing_right = False
        
        # --- PHASE 1: Swoop In (0..24) ---
        if 0 <= orig_f < 25:
            facing_right = False
            t = orig_f / 20.0
            if orig_f < 20:
                bird_x = 300.0 - (1.0 - (1.0 - t) ** 1.8) * 130.0
                bird_y = -35.0 + t * (bird_base_y + 35.0)
                wing_idx = (int(orig_f) // 1) % 4
                bird_sprite_name = f'fly_{wing_idx}'
            elif orig_f < 23:
                bird_x = 170.0
                bird_y = bird_base_y + 2.0
                bird_sprite_name = 'hop_2'
            else:
                bird_x = 170.0
                bird_y = bird_base_y
                bird_sprite_name = 'idle_0'

        # --- PHASE 2: Knock Pencil (25..64) ---
        elif 25 <= orig_f < 65:
            facing_right = True
            if orig_f < 33:
                bird_x = 170.0
                bird_sprite_name = 'alert_0' if orig_f < 29 else 'idle_2_dn'
            elif orig_f < 45:
                w_t = (orig_f - 33) / 12.0
                bird_x = 170.0 + w_t * 26.0
                w_idx = int(orig_f - 33) % 8
                bird_sprite_name = f'waddle_{w_idx}'
            elif orig_f < 49:
                bird_x = 196.0
                bird_sprite_name = 'peck_1'
            elif orig_f < 52:
                bird_x = 194.0
                bird_sprite_name = 'idle_1'
            elif orig_f < 57:
                bird_x = 200.0
                bird_sprite_name = 'peck_2'
            elif orig_f < 61:
                bird_x = 212.0
                bird_sprite_name = 'idle_0_dn'
            else:
                bird_x = 212.0
                b_idx = int(orig_f - 61) % 2
                bird_sprite_name = f'bob_{b_idx}'

        # --- PHASE 3: Knock Bell (65..104) ---
        elif 65 <= orig_f < 105:
            facing_right = False
            if orig_f < 72:
                bird_x = 210.0
                bird_sprite_name = 'alert_0'
            elif orig_f < 84:
                w_t = (orig_f - 72) / 12.0
                bird_x = 210.0 - w_t * 45.0
                w_idx = int(orig_f - 72) % 8
                bird_sprite_name = f'waddle_{w_idx}'
            elif orig_f < 87:
                bird_x = 165.0
                bird_sprite_name = 'peck_0'
            elif orig_f < 93:
                bird_x = 162.0
                dp_idx = int(orig_f - 87) % 4
                bird_sprite_name = f'double_peck_{dp_idx}'
            elif orig_f < 98:
                h_t = (orig_f - 93) / 5.0
                bird_x = 162.0 - h_t * 35.0
                h_idx = int(orig_f - 93) % 4
                bird_sprite_name = f'hop_{h_idx}'
            else:
                bird_x = 127.0
                bird_sprite_name = 'heart_wings_0'

        # --- PHASE 4: Knock Mug with Lowered Head (105..155) ---
        elif 105 <= orig_f < 156:
            facing_right = False
            if orig_f < 114:
                w_t = (orig_f - 105) / 9.0
                bird_x = 127.0 - w_t * 4.0
                w_idx = int(orig_f - 105) % 8
                bird_sprite_name = f'waddle_{w_idx}'
            elif orig_f < 120:
                bird_x = 123.0
                bird_sprite_name = 'bow_0' if orig_f < 117 else 'bow_1'
            elif orig_f < 134:
                push_t = (orig_f - 120) / 14.0
                bird_x = 123.0 - push_t * 35.0
                bird_sprite_name = 'bow_1' if (int(orig_f) // 2) % 2 == 0 else 'bonk_1'
                d.text((int(bird_x - 6), 25), "💦", fill='#38bdf8', font=font_fx)
                d.line([(int(mx + 8), 105), (int(mx + 16), 105)], fill='#78350f', width=2)
            elif orig_f < 138:
                thrust_t = (orig_f - 134) / 4.0
                bird_x = 88.0 - thrust_t * 8.0
                bird_sprite_name = 'bonk_2'
                if 134 <= orig_f <= 137:
                    d.ellipse([(35, 86), (38, 89)], fill='#5c2d16')
                    d.ellipse([(41, 82), (44, 85)], fill='#5c2d16')
            elif orig_f < 147:
                bird_x = 65.0
                bird_sprite_name = 'bow_1' if orig_f < 142 else 'idle_0_dn'
            else:
                bird_x = 65.0
                b_idx = int(orig_f - 147) % 2
                bird_sprite_name = f'bob_{b_idx}'

        # --- PHASE 5: Celebrate & Fly Away (156..199) ---
        else:
            if orig_f < 164:
                facing_right = True
                w_t = (orig_f - 156) / 8.0
                bird_x = 65.0 + w_t * 45.0
                w_idx = int(orig_f - 156) % 8
                bird_sprite_name = f'waddle_{w_idx}'
            elif orig_f < 174:
                facing_right = True
                bird_x = 110.0
                s_idx = int(orig_f - 164) % 3
                bird_sprite_name = f'sing_{s_idx}'
            elif orig_f < 178:
                facing_right = True
                bird_x = 110.0
                bird_y = bird_base_y + 3.0
                bird_sprite_name = 'hop_0'
            else:
                facing_right = True
                fly_t = (orig_f - 178) / 21.0
                bird_x = 110.0 + (fly_t ** 1.3) * 230.0
                bird_y = bird_base_y - (fly_t ** 1.6) * 125.0
                wing_idx = (int(orig_f - 178) // 1) % 4
                bird_sprite_name = f'fly_{wing_idx}'
                d.line([(bird_x - 35, bird_y + 45), (bird_x - 15, bird_y + 45)], fill='#94a3b8', width=1)
                d.line([(bird_x - 45, bird_y + 55), (bird_x - 20, bird_y + 55)], fill='#cbd5e1', width=1)

        # Paste bird sprite
        sp_dict = sprites_r if facing_right else sprites_l
        b_sprite = sp_dict.get(bird_sprite_name, sp_dict['idle_0'])
        frame_img.paste(b_sprite, (int(bird_x - 50), int(bird_y)), b_sprite)
        
        frame_path = os.path.join(out_dir, f"table_mischief_{f}.png")
        frame_img.save(frame_path, "PNG")

    print(f"Successfully generated 400 frames for {crest_type} in {out_dir}.")

if __name__ == '__main__':
    generate_table_mischief_sprites("classic")
    generate_table_mischief_sprites("triple")
