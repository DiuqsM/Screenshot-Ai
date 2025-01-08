import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;

public class ScreenCapture {
    private JFrame frame;
    private Rectangle selection;
    private Point startPoint;
    private JWindow selectionWindow;
    
    public ScreenCapture() {
        // Create transparent full-screen window
        frame = new JFrame();
        frame.setUndecorated(true);
        frame.setAlwaysOnTop(true);
        frame.setBackground(new Color(0, 0, 0, 1));
        
        // Get screen dimensions
        GraphicsEnvironment ge = GraphicsEnvironment.getLocalGraphicsEnvironment();
        GraphicsDevice[] screens = ge.getScreenDevices();
        Rectangle screenBounds = new Rectangle();
        for (GraphicsDevice screen : screens) {
            screenBounds = screenBounds.union(screen.getDefaultConfiguration().getBounds());
        }
        
        frame.setBounds(screenBounds);
        
        // Create selection window with semi-transparent background
        selectionWindow = new JWindow();
        selectionWindow.setBackground(new Color(0, 0, 0, 0.3f));
        selectionWindow.setAlwaysOnTop(true);
        
        // Add mouse listeners
        frame.getContentPane().addMouseListener(new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                startPoint = e.getPoint();
                selection = new Rectangle();
            }
            
            @Override
            public void mouseReleased(MouseEvent e) {
                if (selection != null && selection.width > 0 && selection.height > 0) {
                    captureScreen(selection);
                }
                frame.dispose();
                selectionWindow.dispose();
            }
        });
        
        frame.getContentPane().addMouseMotionListener(new MouseMotionAdapter() {
            @Override
            public void mouseDragged(MouseEvent e) {
                int x = Math.min(startPoint.x, e.getX());
                int y = Math.min(startPoint.y, e.getY());
                int width = Math.abs(e.getX() - startPoint.x);
                int height = Math.abs(e.getY() - startPoint.y);
                
                selection = new Rectangle(x, y, width, height);
                selectionWindow.setBounds(x, y, width, height);
                selectionWindow.setVisible(true);
            }
        });
        
        // Add key listener for escape
        KeyboardFocusManager.getCurrentKeyboardFocusManager().addKeyEventDispatcher(e -> {
            if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
                frame.dispose();
                selectionWindow.dispose();
                return true;
            }
            return false;
        });
        
        // Show the frame
        frame.setVisible(true);
    }
    
    private void captureScreen(Rectangle bounds) {
        try {
            // Create screen capture
            Robot robot = new Robot();
            BufferedImage capture = robot.createScreenCapture(bounds);
            
            // Save to file
            File file = new File("../screenshots");

            File output = File.createTempFile("screenshot", ".png", file);
            System.out.println("Saving to: " + output.getAbsolutePath());
            ImageIO.write(capture, "png", output);
            
            // Show confirmation
            JOptionPane.showMessageDialog(null, 
                "Screenshot saved to: " + output.getAbsolutePath(),
                "Screenshot Captured", 
                JOptionPane.INFORMATION_MESSAGE);
            
        } catch (Exception e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(null,
                "Error capturing screenshot: " + e.getMessage(),
                "Error",
                JOptionPane.ERROR_MESSAGE);
        }
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new ScreenCapture());
    }
}
