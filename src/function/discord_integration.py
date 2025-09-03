import asyncio
import discord
from discord.ext import commands
from ..config import DISCORD_TOKEN, DISCORD_GUILD_ID, DISCORD_CHANNEL_ID, TOTAL_APPS, logger
from ..utils import get_nepal_time


class DiscordBot:
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.ready = False
        self.loop = None
        
        self._setup_events()

    def _setup_events(self):
        @self.bot.event
        async def on_ready():
            self.ready = True
            self.loop = asyncio.get_running_loop()
            logger.info(f'Discord bot logged in as {self.bot.user}')
            
            # Check if bot is in the specified guild
            guild = self.bot.get_guild(DISCORD_GUILD_ID)
            if guild:
                logger.info(f'Bot is in guild: {guild.name} (Members: {guild.member_count})')
                
                # Check if channel exists
                channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
                if channel:
                    logger.info(f'Target channel found: #{channel.name}')
                else:
                    logger.warning(f'Target channel {DISCORD_CHANNEL_ID} not found')
            else:
                logger.warning(f'Bot is not in guild {DISCORD_GUILD_ID}')

    async def create_ipo_embed(self, ipo, rem_days, prob, sug_qty, suggestion):
        """Create Discord embed for IPO alert"""
        
        # Determine color based on probability
        if prob >= 50:
            color = 0x4CAF50  # Green
            prob_indicator = "🟢 High"
        elif prob >= 20:
            color = 0xFF9800  # Orange
            prob_indicator = "🟡 Medium"
        else:
            color = 0xF44336  # Red
            prob_indicator = "🔴 Low"
        
        embed = discord.Embed(
            title=f"🚀 IPO Alert: {ipo['company_name']}",
            description=f"**{ipo['company_name']}** IPO is now open for subscription!",
            color=color,
            timestamp=get_nepal_time()
        )
        
        # Add company info
        embed.add_field(
            name="📊 Basic Information",
            value=f"**Symbol:** {ipo['finid']}\n"
                  f"**Sector:** {ipo.get('Sector', 'N/A')}\n"
                  f"**Issue Manager:** {ipo.get('issue_manager', 'N/A')}",
            inline=True
        )
        
        # Add pricing and dates
        embed.add_field(
            name="💰 Pricing & Timeline",
            value=f"**Offer Price:** NPR {ipo.get('offer_price', 'N/A')}\n"
                  f"**Opening:** {ipo['open_date'].split(' ')[0]}\n"
                  f"**Closing:** {ipo['close_date'].split(' ')[0]}",
            inline=True
        )
        
        # Add shares info
        embed.add_field(
            name="📈 Shares & Time",
            value=f"**Total Shares:** {ipo['shares_offered']:,}\n"
                  f"**Days Remaining:** {rem_days} day{'s' if rem_days != 1 else ''}\n"
                  f"**⏰ Time Left:** {'⚠️ Limited' if rem_days <= 2 else '✅ Available'}",
            inline=True
        )
        
        # Add investment analysis
        embed.add_field(
            name="🎯 Investment Analysis",
            value=f"**Allotment Probability:** {prob_indicator} ({prob:.1f}%)\n"
                  f"**Recommended Quantity:** {sug_qty} units\n"
                  f"**Strategy:** {suggestion}",
            inline=False
        )
        
        # Add action required section
        embed.add_field(
            name="⚡ Action Required",
            value="IPO subscription window is now **OPEN**. Review and submit your application through your broker.",
            inline=False
        )
        
        # Add footer
        embed.set_footer(
            text=f"Based on estimated {TOTAL_APPS:,} total applications • Nepal Time",
            icon_url="https://cdn.discordapp.com/attachments/123456789/chart_icon.png"
        )
        
        # Add thumbnail (you can replace with actual company logo if available)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/123456789/ipo_icon.png")
        
        return embed

    async def send_ipo_alert(self, ipo, rem_days, prob, sug_qty, suggestion):
        """Send Discord alert to the specified channel"""
        try:
            if not self.ready:
                logger.warning("Discord bot not ready, skipping Discord alert")
                return False
            
            channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
            if not channel:
                logger.error(f"Discord channel {DISCORD_CHANNEL_ID} not found")
                return False
            
            embed = await self.create_ipo_embed(ipo, rem_days, prob, sug_qty, suggestion)
            
            # Add @everyone mention for important IPO alerts
            content = "🔔 **IPO ALERT** @everyone" if rem_days <= 3 else "🔔 **IPO ALERT**"
            
            await channel.send(content=content, embed=embed)
            logger.info(f"Discord alert sent for {ipo['company_name']} to #{channel.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Discord alert for {ipo.get('company_name', 'Unknown')}: {e}")
            return False

    async def send_system_notification(self, title, message, notification_type="info"):
        """Send system notifications to Discord"""
        try:
            if not self.ready:
                return False
            
            channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
            if not channel:
                return False
            
            color_map = {
                "success": 0x4CAF50,  # Green
                "info": 0x2196F3,     # Blue
                "warning": 0xFF9800,  # Orange
                "error": 0xF44336     # Red
            }
            
            icon_map = {
                "success": "✅",
                "info": "ℹ️",
                "warning": "⚠️",
                "error": "❌"
            }
            
            color = color_map.get(notification_type, color_map["info"])
            icon = icon_map.get(notification_type, "ℹ️")
            
            embed = discord.Embed(
                title=f"{icon} {title}",
                description=message,
                color=color,
                timestamp=get_nepal_time()
            )
            
            embed.set_footer(text="IPO Alert System • Nepal Time")
            
            await channel.send(embed=embed)
            logger.info(f"Discord system notification sent: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Discord system notification: {e}")
            return False

    def start_bot(self):
        """Start the Discord bot"""
        asyncio.run(self.bot.start(DISCORD_TOKEN))

    def is_ready(self):
        """Check if Discord bot is ready"""
        return self.ready

    def get_loop(self):
        """Get the Discord bot's event loop"""
        return self.loop

    async def close(self):
        """Close the Discord bot"""
        if not self.bot.is_closed():
            await self.bot.close()


# Create a global Discord bot instance
discord_integration = DiscordBot()